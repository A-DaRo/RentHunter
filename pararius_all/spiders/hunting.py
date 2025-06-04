import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from scrapy.loader import ItemLoader
from pararius_all.items import HuntingItem
import time
import logging
from itemloaders.processors import TakeFirst, MapCompose
import re
from datetime import datetime
from scrapy import Request
import os
import pandas as pd
from collections import Counter

logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)


def clean_text(text):
    logging.debug(f"clean_text received: {text} (type: {type(text)})")
    if isinstance(text, (int, float)):
        logging.warning(f"clean_text received numeric value: {text}")
        return text  # Return as-is for numeric values
    if text:
        return re.sub(r'\s+', ' ', text).strip()
    return None
def parse_price(value):
    try:
        return int(re.sub(r'[^\d]', '', value)) if value else None
    except:
        return None

def parse_date(value):
    if value:
        try:
            return datetime.strptime(value, '%d-%m-%Y').date().isoformat()
        except ValueError:
            return None
    return None

def clean_entry(entry):
    if isinstance(entry, str):
        return entry.strip("[]'")  # Remove the square brackets and single quotes
    return entry  # If it's not a string, return it as is

class HousehuntingSpider(scrapy.Spider):
    name = "hunting"
    allowed_domains = ["househunting.nl"]
    start_urls = ["https://househunting.nl/en/housing-offer/?type=for-rent&filter_location=Eindhoven&lat=51.42314229999999&lng=5.462289699999999&street=&km=10&min-price=&max-price="]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'DOWNLOADER_MIDDLEWARES': {
        "scrapy_selenium.SeleniumMiddleware": 800
        },
        'SELENIUM_DRIVER_NAME' : 'chrome',
        'SELENIUM_DRIVER_ARGUMENTS' : ["--headless=new"],
    }

    def __init__(self, *args, **kwargs):
        super(HousehuntingSpider, self).__init__(*args, **kwargs)
        self.existing_urls = self.load_existing_urls()
        self.max_pages = 50
        self.page_count = 0
        self.logger.info(f"Loaded {len(self.existing_urls)} existing URLs from CSV")


    def load_existing_urls(self):
        csv_file = 'hunting_listings.csv'
        if os.path.exists(csv_file):
            urls = set()
            for chunk in pd.read_csv(csv_file, chunksize=1000, usecols=['url']):
                chunk['url'] = chunk['url'].apply(clean_entry)
                urls.update(chunk['url'].dropna().tolist())
            return urls
        return set()

    # Start URLs now use SeleniumRequest to properly initialize Selenium
    def start_requests(self):
        for url in self.start_urls:  # Replace with your actual URL
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=2,  # Optional: default wait time for the Selenium middleware to wait for the initial page load
                screenshot=False  # Set True if you want a screenshot saved in response meta
            )

    def parse(self, response):
        self.logger.info("Opening page with Selenium: %s", response.url)
        driver = response.meta["driver"]

        consecutive_no_change = 0
        previous_count = 0

        # Keep clicking until button disappears or no new listings are loaded
        while True:
            buttons = driver.find_elements(By.CSS_SELECTOR, ".load_more")
            if not buttons:
                self.logger.info("No more 'Show more' button found.")
                break
            
            # Direct JavaScript click
            driver.execute_script("arguments[0].click();", buttons[0])
            self.logger.info("Clicked 'Show more' via JS")
            
            # Short wait for content to load
            time.sleep(5)
            
            # Get updated content count
            sel = Selector(text=driver.page_source)
            listings_scpy = sel.css("li.location a::attr(href)").getall()
            current_count = len(listings_scpy)
            
            if current_count == previous_count:
                consecutive_no_change += 1
            else:
                consecutive_no_change = 0  # Reset counter if new listings appear
            
            previous_count = current_count
            
            if consecutive_no_change >= 1:
                self.logger.info("Stopping due to no new listings after 2 consecutive clicks.")
                break

        # Final scroll to trigger any lazy-loaded content
        ActionChains(driver).scroll_by_amount(0, 3000).perform()
        time.sleep(1)

        # Get final updated content
        sel = Selector(text=driver.page_source)
        listings = sel.css("li.location a::attr(href)").getall()

        def extract_housing_id(url):
            pattern = r"(?<=/)(h\d+-[a-zA-Z-]+)(?=/|$)"
            match = re.search(pattern, url)
            return match.group(0) if match else None

        # Apply the function to the list
        housing_ids = [extract_housing_id(url) for url in listings]

        # Remove duplicates while keeping the first occurrence
        unique_ids = []
        seen = set()
        for id in housing_ids:
            if id not in seen:
                unique_ids.append(id)
                seen.add(id)

        # Reformat the unique IDs into the desired URL format
        formatted_urls = [f"https://househunting.nl/woningaanbod/{id}/" for id in unique_ids]


        print('\nNumber of Listings SCPY:', len(listings))
        print('\nNumber of Listings Formatted:\n', len(formatted_urls))
        for url in formatted_urls:
            if url not in self.existing_urls:
                yield Request(url, callback=self.parse_listing)
    
    # Dutch to English field mapping
    DETAILS_MAPPING = {
        'beschikbaar_per': 'available_from',
        'oppervlakte': 'surface',
        'kamers': 'rooms',
        'slaapkamers': 'bedrooms',
        'badkamers': 'bathrooms',
        'toiletten': 'toilets'
    }

    EXTRAS_MAPPING = {
        'borg': 'deposit',
        'energielabel': 'energy_label',
        'dakterras': 'roof_terrace',
        'interieur': 'interior',
        'locatie': 'location'  # Added location mapping
    }

    def parse_listing(self, response):
        loader = ItemLoader(item=HuntingItem(), response=response)
        loader.default_input_processor = MapCompose(clean_text)
        loader.default_output_processor = TakeFirst()

        # Basic fields
        loader.add_css('title', 'div.single_adress h2::text')
        price = response.css('div.single_price h3::text').re_first(r'(\d+)')
        loader.add_value('price', price)
        
        # Description
        description = ' '.join(response.css('div.house-details__description p::text').getall())
        loader.add_value('description', description)
        
        # Extract details section
        for detail in response.css('ul.details li'):
            text = detail.xpath('text()').get('').strip()
            key = detail.css('span::text').get('').strip().rstrip(':').lower().replace(' ', '_')
            
            if text:
                value = text.split(':', 1)[-1].strip()  # Extract everything after the first colon
            else:
                value = ''

            if key in self.DETAILS_MAPPING:
                eng_key = self.DETAILS_MAPPING[key]
                if eng_key in ['surface', 'rooms', 'bedrooms', 'bathrooms', 'toilets']:  # Numeric fields
                    value = re.sub(r'[^\d]', '', value)  # Remove non-digit characters
                    value = int(value) if value else None
                loader.add_value(eng_key, value)

        
        # Extract extras section
        for extra in response.css('ul.property-extras li'):
            spans = extra.css('span')
            if len(spans) < 2:
                continue
            key_span = spans[0].css('::text').get('').strip().rstrip(':').lower().replace(' ', '_')
            value_span = spans[1].css('::text').get('').strip()
            if key_span in self.EXTRAS_MAPPING:
                eng_key = self.EXTRAS_MAPPING[key_span]
                if eng_key == 'deposit':
                    # Remove currency symbols and convert to integer
                    value = re.sub(r'[^\d]', '', value_span)
                    value = int(value) if value else None
                    loader.add_value(eng_key, value)
                else:
                    loader.add_value(eng_key, value_span)
        
        # Process description for additional fields
        description_data = self.parse_description(description)
        for key, value in description_data.items():
            loader.add_value(key, value)
        
        # Add metadata
        loader.add_value('url', response.url)
        loader.add_value('scraped_at', datetime.now().isoformat())
        
        item = loader.load_item()
        yield item

    def parse_description(self, text):
        patterns = {
            'gas_water_electricity_included': (
                r'(gas/water/electricity|g/w/e|utilities|GWE)\s*(?:are|is)?\s*(not\s+included|excluding|excluded)?',
                lambda m: False if m and m.group(2) else True
            ),
            'service_costs': (
                r'(?:service\s*costs?|monthly\s+prepayment\s+service\s+cost)[\s:]*€\s*([\d,.]+)',
                lambda m: int(float(m.group(1).replace(',', ''))) if m else None
            ),
            'minimum_income': (
                r'(?:income|salary).*?(?:requires?|requirement).*?(\d+)\s*(?:times|months?)',
                lambda m: int(m.group(1)) if m else None
            ),
            'minimal_rent_period': (
                r'rental period minimal (\d+) months?',
                lambda m: int(m.group(1)) if m else None
            ),
            'pets': (
                r'no pets allowed',
                lambda m: False if m else None
            ),
            'smoking': (
                r'no smoking allowed',
                lambda m: False if m else None
            )
        }

        results = {}
        for key, (pattern, processor) in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    results[key] = processor(match)
                except Exception as e:
                    logging.error(f"Error processing {key}: {e}")
        return results