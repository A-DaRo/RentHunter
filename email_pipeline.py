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

pd.options.mode.chained_assignment = None  # Disable the warning

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the root logger level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def spider_closed(spider, reason):
    print(f'{spider.name} has finished crawling. Reason: {reason}')

def process_listings(df_new, df_old, df_name, debug=False):
    if 'URL' in df_new.columns and 'URL' in df_old.columns:
        # Find new listings by comparing URLs
        new_listings = df_new[~df_new['URL'].isin(df_old['URL'])]
        
        if new_listings.empty:
            print(f'No new listings found in {df_name}.')
        else:
            print(f'Found {len(new_listings)} new listings in {df_name}!!! Proceeding to filter and send emails...')
            
            # Apply filtering to new listings
            filtered_listings = filter_listings(new_listings)
            
            if filtered_listings.empty:
                print(f'No new listings in {df_name} meet the filtering criteria.')
            else:
                print(f'Found {len(filtered_listings)} filtered listings in {df_name}. Proceeding to send emails...')
                
                for _, row in filtered_listings.iterrows():
                    send_listing_email(row=row, config=SMTP_CONFIG, debug=debug)
    else:
        print(f'URL column missing in {df_name} DataFrames. Skipping...')

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run the email pipeline.")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Parse the arguments
    args = parser.parse_args()

    print('readind and cleaning old data \n')
    par_df_old = pd.read_csv('pararius_listings.csv')
    par_df_old = clean_data_par(par_df_old)

    hunt_df_old = pd.read_csv('hunting_listings.csv')
    hunt_df_old = clean_data_hunting(hunt_df_old)

    friend_df_old = pd.read_csv('friendlyhousing_listings.csv')
    friend_df_old = clean_data_friend(friend_df_old)

    rot_df_old = pd.read_csv('rotsvast_listings.csv')
    rot_df_old = clean_data_rot(rot_df_old)

    ex_df_old = pd.read_json('extate_listings.json')
    ex_df_old = clean_data_ex(ex_df_old)

    light_df_old = pd.read_json('lightcity_listings.json')
    light_df_old = clean_data_light(light_df_old)

    print('starting to scrape \n')

    # Disable Scrapy's logging
    logging.getLogger('scrapy').setLevel(logging.ERROR)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    # Silence Scrapy and asyncio loggers
    logging.getLogger('pararius').setLevel(logging.ERROR)
    logging.getLogger('friendlyhousing').setLevel(logging.ERROR)
    logging.getLogger('rotsvast').setLevel(logging.ERROR)
    logging.getLogger('hunting').setLevel(logging.ERROR)
    logging.getLogger('extate').setLevel(logging.ERROR)
    logging.getLogger('lightcity').setLevel(logging.ERROR)
    logging.getLogger('asyncio').setLevel(logging.ERROR)

    # prevent log propagation
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('selenium').propagate = False
    logging.getLogger('urllib3').propagate = False
    logging.getLogger('pararius').propagate = False
    logging.getLogger('friendlyhousing').propagate = False
    logging.getLogger('rotsvast').propagate = False
    logging.getLogger('hunting').propagate = False
    logging.getLogger('extate').propagate = False
    logging.getLogger('lightcity').propagate = False
    logging.getLogger('asyncio').propagate = False
    # Enable logging for 'par_login'
    par_login_logger = logging.getLogger('par_login')
    par_login_logger.setLevel(logging.INFO)  # Set the desired logging level
    par_login_logger.propagate = True  # Ensure messages propagate to the root logger
    
    # Get the project settings
    settings = get_project_settings()

    # Create a CrawlerRunner
    runner = CrawlerRunner(settings)

    # Connect the spider_closed function to the spider_closed signal
    dispatcher.connect(spider_closed, signal=signals.spider_closed)

    # Start the initial spiders
    deferred_list = [
        runner.crawl('pararius'),
        runner.crawl('friendlyhousing'),
        runner.crawl('rotsvast'),
        runner.crawl('hunting'),
        runner.crawl('extate'),
        runner.crawl('lightcity')
    ]

    # Wait for all initial spiders to finish
    deferred_all = DeferredList(deferred_list)
    

    # Callback to process results and conditionally start the 'par_login' spider
    def process_results_and_start_par_login(_):
        print('Scraping complete \n')
        print('Reading and cleaning new data \n')

        par_df_new = pd.read_csv('pararius_listings.csv')
        par_df_new = clean_data_par(par_df_new)

        hunt_df_new = pd.read_csv('hunting_listings.csv')
        hunt_df_new = clean_data_hunting(hunt_df_new)

        friend_df_new = pd.read_csv('friendlyhousing_listings.csv')
        friend_df_new = clean_data_friend(friend_df_new)

        rot_df_new = pd.read_csv('rotsvast_listings.csv')
        rot_df_new = clean_data_rot(rot_df_new)

        ex_df_new = pd.read_json('extate_listings.json')
        ex_df_new = clean_data_ex(ex_df_new)

        light_df_new = pd.read_json('lightcity_listings.json')
        light_df_new = clean_data_light(light_df_new)

        # Check if debug mode is enabled
        if args.debug:
            print("Debug mode is ON \n")
            debug_mode = True
        else:
            print("Debug mode is OFF \n")
            debug_mode = False

        # Process Pararius listings
        if 'URL' in par_df_new.columns and 'URL' in par_df_old.columns:
            new_listings = par_df_new[~par_df_new['URL'].isin(par_df_old['URL'])]
            if new_listings.empty:
                print('No new listings found in Pararius.')
            else:
                print(f'Found {len(new_listings)} new listings in Pararius!!! Proceeding to send emails...')
                filtered_listings = filter_listings_par(new_listings)

                if filtered_listings.empty:
                    print(f'No new listings in Pararius meet the filtering criteria.')
                else:
                    print(f'Found {len(filtered_listings)} filtered listings with matching criteria. Proceeding to send emails...')
                    for _, row in filtered_listings.iterrows():
                        send_listing_email(row=row, config=SMTP_CONFIG, debug=debug_mode, pararius=True)

                    # Start the 'par_login' spider if there are filtered listings
                    if not filtered_listings.empty:
                        return runner.crawl('par_login', rows=filtered_listings.to_dict('records'))

        # Process listings for other DataFrames
        process_listings(hunt_df_new, hunt_df_old, 'hunt_df', debug=debug_mode)
        process_listings(friend_df_new, friend_df_old, 'friend_df', debug=debug_mode)
        process_listings(rot_df_new, rot_df_old, 'rot_df', debug=debug_mode)
        process_listings(ex_df_new, ex_df_old, 'ex_df', debug=debug_mode)
        process_listings(light_df_new, light_df_old, 'light_df', debug=debug_mode)

    # Attach the callback to process results and start 'par_login' if needed
    deferred_all.addCallback(process_results_and_start_par_login)

    # Stop the reactor when everything is done
    deferred_all.addBoth(lambda _: reactor.stop())

    # Start the reactor
    reactor.run()

if __name__ == "__main__":
    main()