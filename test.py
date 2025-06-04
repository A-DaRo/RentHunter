import sys
import asyncio
from twisted.internet import asyncioreactor
from twisted.internet.main import installReactor
from twisted.internet.error import ReactorAlreadyInstalledError

# Set the event loop policy to use SelectorEventLoop on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def install_reactor():
    try:
        # Create an instance of the reactor and install it
        reactor_instance = asyncioreactor.AsyncioSelectorReactor()
        installReactor(reactor_instance)
        print("Installed asyncio reactor.")
    except ReactorAlreadyInstalledError:
        existing_reactor = asyncioreactor.AsyncioSelectorReactor._currentReactor
        print(f"Reactor already installed: {existing_reactor.__class__.__name__}")
        if not isinstance(existing_reactor, asyncioreactor.AsyncioSelectorReactor):
            print("Error: Wrong reactor detected. Ensure no other code imports the reactor before this point.")
            sys.exit(1)

# Install the reactor BEFORE any other imports
install_reactor()

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from scrapy import signals
import argparse
import pandas as pd
import logging
from pd_helpers import clean_data_par, clean_data_ex, clean_data_friend, clean_data_hunting, clean_data_rot, clean_data_light, filter_listings, filter_listings_par
from email_sender import send_listing_email, SMTP_CONFIG

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the root logger level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Enable logging for 'par_login'
par_login_logger = logging.getLogger('par_login')
par_login_logger.setLevel(logging.INFO)  # Set the desired logging level
par_login_logger.propagate = True  # Ensure messages propagate to the root logger


par_df_old = pd.read_csv('pararius_listings.csv')
par_df_old = clean_data_par(par_df_old)

# select wanted row with the following url
selected_row = par_df_old[par_df_old['URL'] == 'https://www.pararius.com/apartment-for-rent/eindhoven/238b27c1/heezerweg']

#convert row to dictionary
selected_row_dict = selected_row.to_dict('records')


settings = get_project_settings()

# Create a CrawlerRunner
runner = CrawlerRunner(settings)
deferred_list = [runner.crawl(
    'par_login',
    rows=selected_row_dict
)]

deferred_all = DeferredList(deferred_list)
# Stop the reactor when everything is done
deferred_all.addBoth(lambda _: reactor.stop())

# Start the reactor
reactor.run()

