import logging
import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from pararius_all.items import FriendlyHousingItem
import pandas as pd
import re
import os

def clean_entry(entry):
    if isinstance(entry, str):
        return entry.strip("[]'")  # Remove the square brackets and single quotes
    return entry  # If it's not a string, return it as is

class FriendlyhousingSpider(scrapy.Spider):
    name = "friendlyhousing"
    allowed_domains = ["friendlyhousing.nl"]
    start_urls = ["https://friendlyhousing.nl/en/house-listings/"]
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
    }
    def __init__(self, *args, **kwargs):
        super(FriendlyhousingSpider, self).__init__(*args, **kwargs)
        self.existing_urls = self.load_existing_urls()
        self.logger.info(f"Loaded {len(self.existing_urls)} existing URLs from CSV")

    def load_existing_urls(self):
        csv_file = 'friendlyhousing_listings.csv'
        if os.path.exists(csv_file):
            urls = set()
            for chunk in pd.read_csv(csv_file, chunksize=1000, usecols=['URL']):
                chunk['URL'] = chunk['URL'].apply(clean_entry)
                urls.update(chunk['URL'].dropna().tolist())
            return urls
        return set()
    

    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        }
        for url in self.start_urls:
            yield Request(url, headers=headers, callback=self.parse)
        
    def parse(self, response):

        # Extract listings
        listings_new = response.css('div.house-list-item.new a::attr(href)').getall()
        listings_rented = response.css('div.house-list-item.rented a::attr(href)').getall()
        listings = listings_new + listings_rented

        for listing in listings:
            url = listing.strip()
            if url:
                full_url = response.urljoin(url)
                if full_url not in self.existing_urls:
                    yield Request(full_url, callback=self.parse_listing)


    def parse_listing(self, response):
        loader = ItemLoader(item=FriendlyHousingItem(), response=response)
        
        # Extract core fields with take_first=True to avoid lists.
        loader.add_value('URL', response.url)
        Title = response.css('h1::text').get()
        loader.add_value('Title', Title)
        price = response.css('.price::text').get()  # Extract the text from the SelectorList object
        numbers = re.findall(r'\d+\.?\d*,\d+', price)
        loader.add_value('Price', numbers)
        loader.add_css('Location', 'h1 span::text', take_first=True)
        loader.add_css('Dwelling_type', '.house-type-label::text', take_first=True)
        
        # Price: extract and then remove currency symbols and extra whitespace.

        
        # Price_including_GWL: use text to decide; desired output is a boolean.
        price_incl_text = response.css('.price span::text').get(default='')
        loader.add_value('Price_including_GWL', '(Incl. GWL)' in price_incl_text)
        
        # Process the description HTML.
        description_html = response.css('.house-main__content__description__text').get()
        if description_html:
            parsed_description = parse_description(description_html)
            # Use the cleaned, multi-line text version for Description.
            loader.add_value('Description', parsed_description['full_description'])
            # Also add any extracted key details (e.g. minimum_rental_period) to the item.
            for key, value in parsed_description['key_details'].items():
                loader.add_value(key.capitalize(), value)
        
        # Process the specifications list.
        items = response.css(".house-main__specifications__list__item")
        key_mapping = {
            "Beschikbaar vanaf": "Available from"
        }
        for item in items:
            key = item.css(".house-main__specifications__list__item__title::text").get()
            value = item.css(".house-main__specifications__list__item__value::text").get()
            if key and value:
                key = key.strip()
                value = value.strip()
                # Rename key if applicable and replace spaces with underscores.
                key = key_mapping.get(key, key).replace(' ', '_')
                # For monetary values like Deposit (or Price), remove currency symbols and spaces.
                if key in ['Deposit', 'Price']:
                    value = re.sub(r'[€\$\s]', '', value)
                elif key in ['Surface_area']:
                    value = re.sub(r'\s*m2\s*', '', value)
                loader.add_value(key, value)
        
        yield loader.load_item()


def parse_description(html_content):
        """
        Parse the description HTML and return a dictionary with:
        - full_description: a cleaned, multi-line string of the description
        - key_details: extracted numerical or boolean details based on regex patterns
        """
        response = Selector(text=html_content)
        sections = {}
        order = []
        current_section = None

        # Iterate over all elements in order
        for element in response.css('h2, strong, p, ul'):
            tag = element.root.tag
            if tag in ['h2', 'strong']:
                # When a heading is found, set the current section (strip colon)
                sec = element.xpath('text()').get(default='').strip().replace(':', '')
                if sec:
                    current_section = sec
                    if current_section not in sections:
                        sections[current_section] = []
                        order.append(current_section)
            elif tag == 'ul':
                # If no section has been defined, default to "General"
                if current_section is None:
                    current_section = "General"
                    if current_section not in sections:
                        sections[current_section] = []
                        order.append(current_section)
                # Extract text from each list item
                items = element.css('li::text').getall()
                cleaned = [item.strip() for item in items if item.strip()]
                sections[current_section].extend(cleaned)
            elif tag == 'p':
                if current_section is None:
                    current_section = "General"
                    if current_section not in sections:
                        sections[current_section] = []
                        order.append(current_section)
                text = element.xpath('text()').get(default='').strip()
                if text:
                    sections[current_section].append(text)

        # Reconstruct the full description by joining sections in their original order.
        full_description_lines = []
        for sec in order:
            if sec != "General":
                full_description_lines.append(sec + ":")
            full_description_lines.extend(sections[sec])
            full_description_lines.append("")  # add a blank line between sections
        full_description = "\n".join(full_description_lines).strip()

        # Updated regex patterns – adjust these as needed.
        patterns = {
            'minimum_rental_period': r'(?:minimum|min)(?: rental)? period(?: is)?\s*(\d+)\s*(?:calendar\s*)?months?',
            'utilities_included': r'(?:utilities|gas|water|electricity).*(?:included|includes|including)',
            'furnished': r'\b(furnished|unfurnished)\b',
            'base_rent': r'base rent(?: is)?\s*[€\$]\s*([\d,.]+)',
            'service_costs': r'service costs?(?: is)?\s*[€\$]\s*([\d,.]+)',
            'total_rent': r'total(?: monthly)? rent(?: is)?\s*[€\$]\s*([\d,.]+)',
            'energy_label': r'energy label(?: is)?\s*([A-G][+-]?)',
            'income_requirement': r'income (?:of|needs to be) at least\s*(\d+)x?\s*the rent',
            'maximum_occupancy': r'occupancy (?:of)?\s*by maximum\s*(\d+)\s*people'
        }

        key_details = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, full_description, re.IGNORECASE)
            if match:
                try:
                    if key in ['minimum_rental_period', 'income_requirement', 'maximum_occupancy']:
                        key_details[key] = int(match.group(1))
                    elif key in ['base_rent', 'service_costs', 'total_rent']:
                        # Keep as string so you retain the comma/dot formatting.
                        key_details[key] = match.group(1)
                    elif key == 'utilities_included':
                        key_details[key] = True
                    elif key == 'furnished':
                        key_details[key] = 'unfurnished' not in match.group(1).lower()
                    elif key == 'energy_label':
                        key_details[key] = match.group(1).upper()
                except Exception as e:
                    print(f"Error processing {key}: {e}")

        return {
            'key_details': key_details,
            'full_description': full_description
        }