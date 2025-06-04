import pandas as pd
import numpy as np

'''
Pandas cleaning related helpers functions to support pipeline.py
'''

def clean_entry(entry):
    if isinstance(entry, str):
        return entry.strip("[]'")  # Remove the square brackets and single quotes
    return entry  # If it's not a string, return it as is

agency_data = {
    'kempen-o-g-vastgoedbeheer': {
        'email': 'info@kempen-og.nl',
        'address': 'Geldropseweg 448, 5645 TL EINDHOVEN'
    },
    'nl-homeservice': {
        'email': 'info@nl-homeservice.nl',
        'address': None
    },
    'gohome': {
        'email': 'support@gohome.rent',
        'address': None
    },
    'interhouse-verhuurmakelaars-eindhoven': {
        'email': 'eindhoven.vh@interhouse.nl',
        'address': 'Tramstraat 21-21, 5611 CM Eindhoven'
    },
    'w-heeren-makelaardij': {
        'email': 'info@wheeren.nl',
        'address': None
    },
    'smart-letting': {
        'email': 'info@smartletting.nl',
        'address': 'Nassaustraat 105a, 3601BD MAARSSEN'
    },
    'kievit-makelaardij': {
        'email': 'info@kievitmakelaardij.nl',
        'address': None
    },
    'census-real-estate': {
        'email': 'info@censusrealestate.nl',
        'address': 'Bilderdijklaan 23, 5611 NG Eindhoven'
    },
    'best-intermediair-vastgoed-makelaardij': {
        'email': 'info@bivastgoed.nl',
        'address': 'Valkenswaardseweg 2, 5595 CB Leende, Nederland'
    },
    'brugvast-makelaardij': {
        'email': 'info@brugvast.nl',
        'address': None
    },
    'living-in-holland': {
        'email': 'info@livinginholland.eu',
        'address': None
    },
    'regiis': {
        'email': 'maikel@regiis.nl',
        'address': 'Copernicuslaan 323, 5223 EH, ‘s-Hertogenbosch'
    },
    'stones-housing': {
        'email': 'info@stoneshousing.nl',
        'address': 'Leostraat 63, 5644 PB Eindhoven (NL)'
    },
    'bosscha-makelaardij': {
        'email': 'info@bosschamakelaars.nl',
        'address': 'Lindenstraat 48, Haarlem'
    },
    'liv-housing': {
        'email': 'info@livhousing.nl',
        'address': 'Don Boscostraat 4, 5611 KW Eindhoven'
    },
    'holland2stay': {
        'email': 'info@holland2stay.com',
        'address': None
    },
    'dg-vesta': {
        'email': 'info@dgvesta.nl',
        'address': 'Nachtegaallaan 8, 5611 CV Eindhoven, Nederland'
    },
    'tenant-huurwoningen': {
        'email': 'info@tenant-huurwoningen.nl',
        'address': 'Aalsterweg 89-B, 5615CB EINDHOVEN'
    },
    'goeth-vastgoed': {
        'email': 'info@goethvastgoed.nl',
        'address': 'Jan smitzlaan 4a, 5611 LE Eindhoven'
    },
    'dhvc-vastgoed': {
        'email': 'info@dhvc.nl',
        'address': 'Aalsterweg 224, 5644 RJ Eindhoven, Nederland'
    },
    'housing-totaal': {
        'email': 'info@housingtotaal.nl',
        'address': 'Hertogstraat 27, 5611 PA Eindhoven'
    },
    '123wonen-eindhoven': {
        'email': 'eindhoven@123wonen.nl',
        'address': 'Croy 7, 5653 LC Eindhoven'
    },
    'viadaan': {
        'email': 'info@viadaan.nl',
        'address': 'Fellenoord 39, Eindhoven 5612 AA'
    },
    'stoit-groep': {
        'email': 'eindhoven@stoit.nl',
        'address': 'De Regent 6, 5611 HW Eindhoven'
    },
    'my-housing': {
        'email': 'info@myhousing.nl',
        'address': 'Geldropseweg 86C, 5611 SK Eindhoven'
    },
    'huurinc-housing': {
        'email': 'info@huurinc.nl',
        'address': 'Wilhelminaplein 15, 5611 HE Eindhoven, Netherlands'
    },
    'zuid-beheer-b-v': {
        'email': 'info@zuidbeheer.nl',
        'address': 'Torenallee 57, 5617 BB Eindhoven'
    },
    'ki-makelaardij': {
        'email': 'contact@ki-makelaardij.nl',
        'address': 'Croy 7c, 5653LC Eindhoven, Nederland'
    },
    'r56-makelaars-en-huisvesting': {
        'email': 'info@r56.nl',
        'address': 'Bleekstraat 31, 5611 VB Eindhoven, Nederland'
    },
    'househunting-eindhoven': {
        'email': 'eindhoven@househunting.nl',
        'address': 'Hoogstraat 14, 5611JR Eindhoven'
    },
    'lemon-suites': {
        'email': 'home@lemonsuites.nl',
        'address': 'Torenallee 65, 5617 BB Eindhoven'
    },
    'lightcity-housing': {
        'email': 'info@lightcityhousing.nl',
        'address': 'Leenderweg 36 A, 5615 AA Eindhoven'
    },
    'brick-vastgoed': {
        'email': 'info@brickvastgoed.nl',
        'address': 'Bergstraat 24, 5611 JZ Eindhoven'
    },
    'friendly-housing': {
        'email': 'info@friendlyhousing.nl',
        'address': 'Cassandraplein 55, 5631 BA Eindhoven'
    },
    'extate-housing': {
        'email': 'info@extatehousing.nl',
        'address': 'Woenselse Markt 3, 5612 CP Eindhoven'
    },
    'rotsvast-eindhoven': {
        'email': 'eindhoven@rotsvast.nl',
        'address': 'Willemstraat 14, 5611 HD Eindhoven'
    },
    'w-en-d-vastgoed': {
        'email': 'verhuur@wdvastgoed.nl',
        'address': 'Postbus 96, 5580 AB, Waalre'
    }
}


def clean_data_par(df):
    bug_columns = [
        'Agency_Link', 'Available_From', 'Balcony', 'Construction_Type', 'Construction_Year',
        'Contract_Type', 'Deposit', 'Description', 'Energy_Rating', 'Facilities', 'Form_link', 'Garage_Present',
        'Garden', 'House_Type', 'Interior', 'Latitude', 'Living_Area', 'Location', 'Longitude',
        'Number_of_Bathrooms', 'Number_of_Floors', 'Number_of_Rooms', 'Offered_Since',
        'Parking_Present', 'Parking_Type', 'Pets_Allowed', 'Rent_Price', 'Service_Costs',
        'Shed_Storeroom', 'Smoking_Allowed', 'Status', 'Title', 'URL', 'Upkeep'
    ]
    mask = df.isin(bug_columns).any(axis=1)
    df = df[~mask]
    # Reset index to avoid alignment issues
    df = df.reset_index(drop=True)
    df = df.map(clean_entry)
    df['Available_From'] = pd.to_datetime(df['Available_From'], errors='coerce')
    df['Construction_Year'] = pd.to_numeric(df['Construction_Year'], errors='coerce')
    df['Deposit'] = df['Deposit'].replace('NaN', None).str.replace(',', '').astype(float)
    df['Energy_Rating'] = df['Energy_Rating'].astype('category')
    df['Rent_Price'] = df['Rent_Price'].replace('NaN', None).str.replace(',', '').astype(float)
    df['Living_Area'] = df['Living_Area'].replace('NaN', None).str.replace(',', '').astype(float)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Title'] = df['Title'].str.replace('For rent:', '', regex=False).str.strip()
    df['Agency_Name'] = df['Agency_Link'].str.extract(r'([^/]+)$')
    df['Agency_Email'] = df['Agency_Name'].apply(lambda x: agency_data.get(x, {}).get('email', None))
    #df['Agency_Email'] = None
    df['Agency_Address'] = df['Agency_Name'].apply(lambda x: agency_data.get(x, {}).get('address', None))
    
    return df

def clean_data_ex(df):

    rent_mask = df['isRentals'] == True
    city_mask = df['city'] == 'Eindhoven'
    df = df[rent_mask & city_mask]
    df.rename(columns={'rentalsPrice': 'Rent_Price', 'livingSurface': 'Living_Area', 'rooms': 'Number_of_Rooms', 'url': 'URL'}, inplace=True)
    df["Title"] = df['address'] + ", " + df['zipcode'] + " in " + df['city']
    df['Agency_Name'] = 'extate-housing'
    df['Agency_Email'] = 'info@extatehousing.nl'
    df['Agency_Address'] = 'Woenselse Markt 3, 5612 CP Eindhoven'

    return df

def clean_data_light(df):

    rent_mask = df['isRentals'] == True
    city_mask = df['city'] == 'Eindhoven'
    df = df[rent_mask & city_mask]
    df.rename(columns={'rentalsPrice': 'Rent_Price', 'livingSurface': 'Living_Area', 'rooms': 'Number_of_Rooms', 'url': 'URL'}, inplace=True)
    df["Title"] = df['address'] + ", " + df['zipcode'] + " in " + df['city']
    df['Agency_Name'] = 'lightcity-housing'
    df['Agency_Email'] = 'info@lightcityhousing.nl'
    df['Agency_Address'] = 'Leenderweg 36 A, 5615 AA Eindhoven'

    return df

def clean_data_hunting(df):

    bug_columns = ['available_from', 'bathrooms', 'bedrooms', 'deposit', 'description', 'energy_label', 'gas_water_electricity_included', 'interior', 'location',
                   'minimal_rent_period', 'minimum_income', 'pets', 'price', 'roof_terrace', 'rooms', 'scraped_at', 'service_costs', 'smoking', 'surface', 'title',
                   'toilets', 'url']
    
    mask = df.isin(bug_columns).any(axis=1)
    df = df[~mask]

    df.rename(columns={'price': 'Rent_Price', 'surface': 'Living_Area', 'title': 'Title', 'url': 'URL', 'rooms': 'Number_of_Rooms'}, inplace=True)
    df['Agency_Name'] = 'househunting-eindhoven'
    df['Agency_Email'] = 'eindhoven@househunting.nl'
    df['Agency_Address'] = 'Hoogstraat 14, 5611JR Eindhoven'

    return df

def clean_data_friend(df):

    bug_columns = ['Available_from', 'Base_rent', 'City', 'Deposit', 'Description', 'Dwelling_type', 'Energy_label', 'Furnished', 'Income_requirement', 'Location', 'Maximum_occupancy',
                   'Minimum_rental_period', 'Number_of_bedrooms', 'Number_of_rooms', 'Postal_code', 'Price', 'Price_including_GWL', 'Service_costs', 'Surface_area',
                   'Title', 'Total_rent', 'URL', 'Utilities_included']
    
    mask = df.isin(bug_columns).any(axis=1)
    df = df[~mask]
    df = df.map(clean_entry)
    df.rename(columns={'Price': 'Rent_Price', 'Surface_area': 'Living_Area', 'Number_of_rooms':'Number_of_Rooms'}, inplace=True)
    df['Agency_Name'] = 'friendly-housing'
    df['Agency_Email'] = 'info@friendlyhousing.nl'
    df['Agency_Address'] = 'Cassandraplein 55, 5631 BA Eindhoven'

    return df

def clean_data_rot(df):

    bug_columns = ['Agency_Link', 'Bedrooms', 'Deposit', 'Description', 'Energy_Label', 'Floor_Area', 'Interior', 'Latitude', 'Location', 'Longitude', 'Other_Costs', 'Pets',
                   'Rent_Price', 'Rooms', 'Service_Costs', 'Smoking', 'Start_Date', 'Title', 'Total_Rent', 'Transfer_Costs', 'Type', 'URL', 'Utilities']
    
    mask = df.isin(bug_columns).any(axis=1)
    df = df[~mask]
    df = df.map(clean_entry)
    df.rename(columns={'Floor_Area': 'Living_Area', 'Rooms': 'Number_of_Rooms'}, inplace=True)
    df['Title'] = df['Title'].str.replace('?', '', regex=False).str.strip()
    df['Agency_Name'] = 'rotsvast-eindhoven'
    df['Agency_Email'] = 'eindhoven@rotsvast.nl'
    df['Agency_Address'] = 'Willemstraat 14, 5611 HD Eindhoven'

    return df

def filter_listings(df):

# Function to clean and convert the Rent_Price column
    df['Rent_Price'] = (
        df['Rent_Price']
        .astype(str)  # Convert to string to safely use .str.replace()
        .str.replace('.', '', regex=False)  # Remove thousand separators (dots)
        .str.replace(',', '.', regex=False)  # Replace comma with dot for decimal
        .replace('nan', np.nan)  # Replace string 'nan' with actual NaN
        .astype(float)  # Convert to float first to handle decimals
        .astype('Int64')  # Convert to nullable integer type (handles NaN)
    )

    df['Living_Area'] = df['Living_Area'].fillna(0).astype(int)

    price_mask = df['Rent_Price'] <= 700
    surface_mask = df['Living_Area'] >= 15

    return df[price_mask & surface_mask]
    
def filter_listings_par(df):

    price_mask = df['Rent_Price'] <= 700
    surface_mask = df['Living_Area'] >= 11

    return df[price_mask & surface_mask]
    
    