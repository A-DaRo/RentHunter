import logging
import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from pararius_all.items import ParariusItem
import pandas as pd
import os

class ParariusSpider(scrapy.Spider):
    name = "pararius"
    allowed_domains = ["pararius.com"]
    start_urls = ["https://www.pararius.com/apartments/eindhoven"]
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
    }

    def __init__(self, *args, **kwargs):
        super(ParariusSpider, self).__init__(*args, **kwargs)
        self.existing_urls = self.load_existing_urls()
        self.max_pages = 50
        self.page_count = 0
        self.logger.info(f"Loaded {len(self.existing_urls)} existing URLs from CSV")

    def load_existing_urls(self):
        csv_file = 'pararius_listings.csv'
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
        self.page_count += 1
        if self.page_count > self.max_pages:
            self.logger.info(f"Reached maximum page limit: {self.max_pages}")
            return

        # Extract listings
        listings = response.css('a.listing-search-item__link--depiction::attr(href)').getall()
        self.logger.info(f"Found {len(listings)} listings on page {self.page_count}")

        for listing in listings:
            url = listing.strip()
            if url:
                full_url = response.urljoin(url)
                if full_url not in self.existing_urls:
                    yield Request(full_url, callback=self.parse_listing)

        # Extract next page
        next_page = response.css('li.pagination__item--next a.pagination__link--next::attr(href)').get()
        if next_page:
            next_url = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_url}")
            yield Request(next_url, callback=self.parse)
        else:
            self.logger.info("No more pages found")
    
    def parse_listing(self, response):
        loader = ItemLoader(item=ParariusItem(), response=response)  # Use ParariusItem instead of DynamicItem
        
        # Extract core fields
        loader.add_value('URL', response.url)
        loader.add_css('Title', 'div.listing-detail-summary__primary-information h1.listing-detail-summary__title::text')
        loader.add_css('Location', 'div.listing-detail-summary__primary-information div.listing-detail-summary__location::text')
        loader.add_css('Description', 'div.listing-detail-description__content div.listing-detail-description__additional ::text')
        loader.add_css('Agency_Link', 'a.agent-summary__link.agent-summary__link--agent-page::attr(href)')
        base_link = 'https://www.pararius.com'
        loader.add_value('Form_link', base_link + response.css('a.listing-reaction-button.listing-reaction-button--contact-agent::attr(href)').get())
        loader.add_css('Latitude', 'wc-detail-map::attr(data-latitude)')
        loader.add_css('Longitude', 'wc-detail-map::attr(data-longitude)')

                # Extract additional details
        # Existing rules with modifications
        loader.add_css('Rent_Price', 'dt:contains("Rental price") + dd span.listing-features__main-description::text', re=r'€\s*([\d.,]+)')
        loader.add_css('Offered_Since', 'dt:contains("Offered since") + dd span.listing-features__main-description::text', re=r'(\d{2}-\d{2}-\d{4})')
        loader.add_css('Status', 'dt:contains("Status") + dd span.listing-features__main-description::text')
        loader.add_css('Available_From', 'dt:contains("Available") + dd span.listing-features__main-description::text', re=r'(?:From\s*)?(\d{2}-\d{2}-\d{4}|Immediately)')
        loader.add_css('Contract_Type', 'dt:contains("Rental agreement") + dd span.listing-features__main-description::text')
        loader.add_css('Deposit', 'dt:contains("Deposit") + dd span.listing-features__main-description::text', re=r'€\s*([\d.,]+)')
        loader.add_css('Interior', 'dt:contains("Interior") + dd span.listing-features__main-description::text')
        # New additions for updated structure
        loader.add_css('Upkeep', 'dt:contains("Upkeep") + dd span.listing-features__main-description::text')
        loader.add_css('Service_Costs', 'dt:contains("Rental price") + dd ul.listing-features__sub-description li::text', re=r'(Includes|Excludes):\s*(.*)')
        loader.add_css('Living_Area', 'dt:contains("Living area") + dd span.listing-features__main-description::text', re=r'(\d+)\s*m²')
        # Extract Type of House
        loader.add_css('House_Type', 'dt:contains("Type of house") + dd span.listing-features__main-description::text')
        # Extract Type of Construction
        loader.add_css('Construction_Type', 'dt:contains("Type of construction") + dd span.listing-features__main-description::text')
        # Extract Year of Construction
        loader.add_css('Construction_Year', 'dt:contains("Year of construction") + dd span.listing-features__main-description::text', re=r'(\d{4})')
        # Extract Location (multiple items)
        loader.add_css('Location', 'dt:contains("Location") + dd ul.listing-features__main-description li::text')
        # Extract Number of Rooms
        loader.add_css('Number_of_Rooms', 'dt:contains("Number of rooms") + dd span.listing-features__main-description::text')
        # Extract Number of Bathrooms
        loader.add_css('Number_of_Bathrooms', 'dt:contains("Number of bathrooms") + dd span.listing-features__main-description::text')
        # Extract Number of Floors
        loader.add_css('Number_of_Floors', 'dt:contains("Number of floors") + dd span.listing-features__main-description::text')
        # Extract Facilities (multiple items)
        loader.add_css('Facilities', 'dt:contains("Facilities") + dd ul.listing-features__main-description li::text')
        # Extract Balcony information
        loader.add_css('Balcony', 'dt:contains("Balcony") + dd span.listing-features__main-description::text')
        # Extract Garden information
        loader.add_css('Garden', 'dt:contains("Garden") + dd span.listing-features__main-description::text')
        # Extract Energy Rating
        loader.add_css('Energy_Rating', 'dt:contains("Energy rating") + dd span.listing-features__main-description::text')
        loader.add_css('Shed_Storeroom', 'dt:contains("Shed/Storeroom") + dd span.listing-features__main-description::text')
        loader.add_css('Parking_Present', 'dt:contains("Present") + dd span.listing-features__main-description::text')
        loader.add_css('Parking_Type', 'dt:contains("Type of parking") + dd span.listing-features__main-description::text')	
        loader.add_css('Garage_Present', 'dt:contains("Present") + dd span.listing-features__main-description::text')
        loader.add_css('Smoking_Allowed', 'dt:contains("Smoking allowed") + dd span.listing-features__main-description::text')
        loader.add_css('Pets_Allowed', 'dt:contains("Pets allowed") + dd span.listing-features__main-description::text')
        # Load and validate item
        item = loader.load_item()
        
        # Verify required fields
        required_fields = ['Title', 'Location', 'Description']
        for field in required_fields:
            if not item.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        yield item




def clean_entry(entry):
    if isinstance(entry, str):
        return entry.strip("[]'")  # Remove the square brackets and single quotes
    return entry  # If it's not a string, return it as is