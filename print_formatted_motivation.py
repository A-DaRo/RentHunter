import pandas as pd
import logging
from pd_helpers import clean_data_par, clean_data_ex, clean_data_friend, clean_data_hunting, clean_data_rot, clean_data_light, filter_listings, filter_listings_par
from email_sender import send_listing_email, SMTP_CONFIG

print('readind and cleaning old data \n')
par_df_old = pd.read_csv('pararius_listings.csv')
par_df_old = clean_data_par(par_df_old)

# select last row
selected_row = par_df_old.iloc[-1]

motivation_template_file = 'Your_Motivation_Template.txt' # Ensure the template file exists

row = selected_row.to_dict()

with open(motivation_template_file, 'r') as f:
    motivation_template = f.read()

row_data = {k: ("" if v is None else v) for k, v in row.items()}
motivation_text = motivation_template.format(**row_data)

print(motivation_text)