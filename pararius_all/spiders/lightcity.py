import scrapy
from scrapy import Request
import json


class LightcitySpider(scrapy.Spider):
    name = "lightcity"
    allowed_domains = ["lightcityhousing.nl"]
    start_urls = ["https://www.lightcityhousing.nl/en/realtime-listings/consumer"]
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
    }
    
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
        new_data = response.json()  # Parse the JSON content
        file_path = "lightcity_listings.json" 
        try:
            with open(file_path, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []  # Initialize as an empty list if the file doesn't exist

        new_entries = [entry for entry in new_data if entry not in existing_data]
        if new_entries:
            existing_data.extend(new_entries)

        #Save the updated JSON file
        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)  # Save with pretty formatting