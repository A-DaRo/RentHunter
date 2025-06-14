# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParariusItem(scrapy.Item):
    # Mandatory fields
    URL = scrapy.Field()
    Title = scrapy.Field()
    Location = scrapy.Field()
    Description = scrapy.Field()
    Agency_Link = scrapy.Field()
    Form_link = scrapy.Field()
    Latitude = scrapy.Field()
    Longitude = scrapy.Field()
    Rent_Price = scrapy.Field()
    Offered_Since = scrapy.Field()
    Status = scrapy.Field()
    Available_From = scrapy.Field()
    Contract_Type = scrapy.Field()
    Deposit = scrapy.Field()
    Interior = scrapy.Field()
    Upkeep = scrapy.Field()
    Service_Costs = scrapy.Field()
    Living_Area = scrapy.Field()
    House_Type = scrapy.Field()
    Construction_Type = scrapy.Field()
    Construction_Year = scrapy.Field()
    Number_of_Rooms = scrapy.Field()
    Number_of_Bathrooms = scrapy.Field()
    Number_of_Floors = scrapy.Field()
    Facilities = scrapy.Field()
    Balcony = scrapy.Field()
    Garden = scrapy.Field()
    Energy_Rating = scrapy.Field()
    Shed_Storeroom = scrapy.Field()
    Parking_Present = scrapy.Field()
    Parking_Type = scrapy.Field()
    Garage_Present = scrapy.Field()
    Smoking_Allowed = scrapy.Field()
    Pets_Allowed = scrapy.Field()


class FriendlyHousingItem(scrapy.Item):
    # Mandatory fields
    URL = scrapy.Field()
    Title = scrapy.Field()
    Location = scrapy.Field()
    Description = scrapy.Field()
    Dwelling_type = scrapy.Field()
    Price = scrapy.Field()
    Price_including_GWL = scrapy.Field()
    Description = scrapy.Field()
    Postal_code = scrapy.Field()
    City = scrapy.Field()
    Number_of_rooms = scrapy.Field()
    Available_from = scrapy.Field()
    Surface_area = scrapy.Field()
    Deposit = scrapy.Field()
    Number_of_bedrooms = scrapy.Field()
    Minimum_rental_period = scrapy.Field()
    Utilities_included = scrapy.Field()
    Furnished = scrapy.Field()
    Base_rent = scrapy.Field()
    Service_costs = scrapy.Field()
    Total_rent = scrapy.Field()
    Energy_label = scrapy.Field()
    Income_requirement = scrapy.Field()
    Maximum_occupancy = scrapy.Field()
    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = scrapy.Field()
        super().__setitem__(key, value)


class RotsvastItem(scrapy.Item):
    URL = scrapy.Field()
    Title = scrapy.Field()
    Location = scrapy.Field()
    Description = scrapy.Field()
    Agency_Link = scrapy.Field()
    Latitude = scrapy.Field()
    Longitude = scrapy.Field()
    Rent_Price = scrapy.Field()
    Start_Date = scrapy.Field()
    Total_Rent = scrapy.Field()
    Service_Costs = scrapy.Field()
    Utilities = scrapy.Field()
    Deposit = scrapy.Field()
    Other_Costs = scrapy.Field()
    Transfer_Costs = scrapy.Field()
    Energy_Label = scrapy.Field()
    Type = scrapy.Field()
    Interior = scrapy.Field()
    Rooms = scrapy.Field()
    Bedrooms = scrapy.Field()
    Floor_Area = scrapy.Field()
    Smoking = scrapy.Field()
    Pets = scrapy.Field()



class HuntingItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    available_from = scrapy.Field()
    surface = scrapy.Field()
    rooms = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    toilets = scrapy.Field()  # Add this field
    deposit = scrapy.Field()
    energy_label = scrapy.Field()
    roof_terrace = scrapy.Field()
    interior = scrapy.Field()
    location = scrapy.Field()
    gas_water_electricity_included = scrapy.Field()
    service_costs = scrapy.Field()
    minimum_income = scrapy.Field()
    minimal_rent_period = scrapy.Field()
    pets = scrapy.Field()
    smoking = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()


class FundaItem(scrapy.Item):
    Listing_Type = scrapy.Field()
    URL = scrapy.Field()
    Street_Address = scrapy.Field()
    Neighborhood_Identifier = scrapy.Field()
    City = scrapy.Field()
    Postcode = scrapy.Field()
    House_Number = scrapy.Field()
    Province = scrapy.Field()
    Country = scrapy.Field()
    Is_International = scrapy.Field()
    Description = scrapy.Field()
    Features = scrapy.Field()
    Neighborhood_Name = scrapy.Field()
    Neighborhood_City = scrapy.Field()
    Neighborhood_Residents = scrapy.Field()
    Neighborhood_Family_With_Children = scrapy.Field()
    Neighborhood_Avg_Asking_Price_Per_m2 = scrapy.Field()
    Neighborhood_URL = scrapy.Field()
    Google_Maps_Address = scrapy.Field()
    Agent_Name = scrapy.Field()
    Agent_Profile_URL = scrapy.Field()
    Agent_Phone = scrapy.Field()
    Contact_Agent_URL = scrapy.Field()
    Request_Viewing_URL = scrapy.Field()