import logging
import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from pararius_all.items import RotsvastItem
import pandas as pd
import os
import re


class RotsvastSpider(scrapy.Spider):
    name = "rotsvast"
    allowed_domains = ["www.rotsvast.nl"]
    start_urls = ["https://www.rotsvast.nl/en/property-listings/?type=2&city=Eindhoven&distance=10&office=0"]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
    }

    def __init__(self, *args, **kwargs):
        super(RotsvastSpider, self).__init__(*args, **kwargs)
        self.existing_urls = self.load_existing_urls()
        self.max_pages = 50
        self.page_count = 0
        self.logger.info(f"Loaded {len(self.existing_urls)} existing URLs from CSV")

    def load_existing_urls(self):
        csv_file = 'rotsvast_listings.csv'
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
        listings = response.css('div.residence-gallery.clickable-parent.col-md-4 a::attr(href)').getall()
        self.logger.info(f"Found {len(listings)} listings on page {self.page_count}")

        for listing in listings:
            url = listing.strip()
            if url:
                full_url = response.urljoin(url)
                if full_url not in self.existing_urls:
                    yield Request(full_url, callback=self.parse_listing)
        
        base_url = self.start_urls[0]
        # Extract next page
        next_page_button = response.css('div.multipage a.next::attr(href)').get()
        if next_page_button:
            if "page=" in base_url:
                # Replace existing page parameter
                next_url = re.sub(r"page=\d+", next_page_button.lstrip("?"), next_url)
            else:
                # Add page parameter
                separator = "&" if "?" in base_url else "?"
                next_url = f"{base_url}{separator}{next_page_button.lstrip('?')}"
            self.logger.info(f"Following next page: {next_url}")
            yield Request(next_url, callback=self.parse)
        else:
            self.logger.info("No more pages found")

    
    def parse_listing(self, response):
        
        loader = ItemLoader(item=RotsvastItem(), response=response)  # Use ParariusItem instead of DynamicItem
        
        # Extract core fields
        loader.add_value('URL', response.url)
        loader.add_css('Title', 'h1::text', re_replace=[(r'\?', '')])
        loader.add_css('Location', 'div#breadcrumbs::text', re_replace=[(r'> Property listings >', ''), (r'\?', '')])
        loader.add_css('Description', 'div#description p::text')
        loader.add_value('Agency_Link', 'https://www.rotsvast.nl/en/')  # Assuming the agency link is always the same
        loader.add_css('Latitude', 'div.residence-map iframe::attr(src)', re=r'@(-?\d+\.\d+)')
        loader.add_css('Longitude', 'div.residence-map iframe::attr(src)', re=r'@-?\d+\.\d+,(-?\d+\.\d+)')

        # Extract additional details
        loader.add_css('Rent_Price', 'div#info-price::text', re=r'€\s*([\d.,]+)\s*per month')
        # Extract Start Date
        start_date_xpath = '//div[@id="properties"]//div[contains(text(), "Start date")]/following-sibling::div[last()]//text()'
        start_date = response.xpath(start_date_xpath).get()
        if start_date:
            start_date = re.search(r'(\d{2}-\d{2}-\d{4})', start_date).group(1)
        loader.add_value('Start_Date', start_date)

        # Extract Total Rent
        total_rent_xpath = '//div[@id="properties"]//div[contains(text(), "Total rent")]/following-sibling::div[last()]//text()'
        total_rent = response.xpath(total_rent_xpath).get()
        total_rent = re.search(r'\b(\d+)\b', total_rent).group(1)
        loader.add_value('Total_Rent', total_rent)

        # Extract Service Costs
        service_cost_xpath = '//div[@id="properties"]//div[contains(text(), "Service costs")]/following-sibling::div[last()]//text()'
        service_cost = response.xpath(service_cost_xpath).get()

        if service_cost:
            match = re.search(r'€\s*(\d+)', service_cost)
            service_cost = match.group(1) if match else None

        loader.add_value('Service_Costs', service_cost)

        # Extract Utilities
        utilities_xpath = '//div[@id="properties"]//div[contains(text(), "Utilities")]/following-sibling::div[last()]//text()'
        utilities = response.xpath(utilities_xpath).get()
        if utilities:
            try:
                utilities = re.search(r'€\s*(\d+)', utilities).group(1)
            except AttributeError:
                utilities = None
        loader.add_value('Utilities', utilities)

        # Extract Deposit
        deposit_xpath = '//div[@id="properties"]//div[contains(text(), "Deposit")]/following-sibling::div[last()]//text()'
        deposit = response.xpath(deposit_xpath).get()
        if deposit:
            try:
                deposit = re.search(r'€\s*(\d+)', deposit).group(1)
            except AttributeError:
                deposit = None
        loader.add_value('Deposit', deposit)

        # Extract Service Cost
        service_cost_xpath = '//div[@id="properties"]//div[contains(text(), "Service costs")]/following-sibling::div[last()]//text()'
        service_cost = response.xpath(service_cost_xpath).get()
        if service_cost:
            try:
                service_cost = re.search(r'€\s*(\d+)', service_cost).group(1)
            except AttributeError:
                service_cost = None
        loader.add_value('Service_Costs', service_cost)

        # Extract Other Costs
        other_costs_xpath = '//div[@id="properties"]//div[contains(text(), "Other costs")]/following-sibling::div[last()]//text()'
        other_costs = response.xpath(other_costs_xpath).get()
        if other_costs:
            try:
                other_costs = re.search(r'€\s*(\d+)', other_costs).group(1)
            except AttributeError:
                other_costs = None
        loader.add_value('Other_Costs', other_costs)

        #Extract Transfer Costs
        transfer_costs_xpath = '//div[@id="properties"]//div[contains(text(), "Transfer costs")]/following-sibling::div[last()]//text()'
        transfer_costs = response.xpath(transfer_costs_xpath).get()
        if transfer_costs:
            try:
                transfer_costs = re.search(r'€\s*(\d+)', transfer_costs).group(1)
            except AttributeError:
                transfer_costs = None
        loader.add_value('Transfer_Costs', transfer_costs)

        # Extract Energy Label
        energy_label_xpath = '//div[@id="properties"]//div[contains(text(), "Energy label")]/following-sibling::div[last()]//span[@class="energyLabel"]//text()'
        energy_label = response.xpath(energy_label_xpath).get()
        if energy_label:
            try:
                energy_label = re.search(r'\b([A-G])\b', energy_label).group(1)
            except AttributeError:
                energy_label = None
        loader.add_value('Energy_Label', energy_label)

        # Extract Type
        type_xpath = '//div[@id="properties"]//div[contains(text(), "Type")]/following-sibling::div[last()]//text()'
        loader.add_xpath('Type', type_xpath)

        # Extract Interior
        interior_xpath = '//div[@id="properties"]//div[contains(text(), "Interior")]/following-sibling::div[last()]//text()'
        loader.add_xpath('Interior', interior_xpath)

        # Extract Rooms
        rooms_xpath = '//div[@id="properties"]//div[contains(text(), "Rooms")]/following-sibling::div[last()]//text()'
        rooms = response.xpath(rooms_xpath).get()
        if rooms:
            rooms = re.search(r'\b(\d+)\b', rooms).group(1)
            loader.add_xpath('Rooms', rooms)

        # Extract Bedrooms
        bedrooms_xpath = '//div[@id="properties"]//div[contains(text(), "Bedrooms")]/following-sibling::div[last()]//text()'
        bedrooms = response.xpath(bedrooms_xpath).get()
        if bedrooms:
            bedrooms = re.search(r'\b(\d+)\b', bedrooms).group(1)
        loader.add_xpath('Bedrooms', bedrooms)

        # Extract Floor Area
        floor_area_xpath = '//div[@id="properties"]//div[contains(text(), "Floor area")]/following-sibling::div[last()]//text()'
        floor_area = response.xpath(floor_area_xpath).get()
        if floor_area:
            floor_area = re.search(r'\b(\d+)\b', floor_area).group(1)
        loader.add_value('Floor_Area', floor_area)

        # Extract Smoking
        smoking_xpath = '//div[@id="properties"]//div[contains(text(), "Smoking")]/following-sibling::div[last()]//text()'
        loader.add_xpath('Smoking', smoking_xpath, re=r'\b(Yes|No)\b')

        # Extract Pets
        pets_xpath = '//div[@id="properties"]//div[contains(text(), "Pets")]/following-sibling::div[last()]//text()'
        loader.add_xpath('Pets', pets_xpath)

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



