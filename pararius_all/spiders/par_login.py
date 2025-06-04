from httpcore import TimeoutException
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import random

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the root logger level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('scrapy').propagate = False
logging.getLogger('selenium').propagate = False
logging.getLogger('urllib3').propagate = False

class ParLoginSpider(scrapy.Spider):
    name = "par_login"
    allowed_domains = ["pararius.com"]
    start_urls = ['https://www.pararius.com/login-email']

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

    def __init__(self, rows=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = rows or []
        self.processed_rows = []

    def start_requests(self):
        """Start the request using Selenium"""
        for url in self.start_urls:

            yield SeleniumRequest(
                url=url,
                callback=self.handle_login,
                wait_time=10,  # Wait for the page to load
                meta={'rows': self.rows}  # Pass rows through meta
            )


    def handle_login(self, response):
        """Perform login with persistent session"""

        driver = response.request.meta['driver']
        rows = response.meta['rows']
        print('Handling login')
        try:
            # Try to dismiss any overlays/cookie banners first
            try:
                # Common overlay/cookie selectors to try
                overlay_selectors = [
                    (By.ID, "_vis_opt_path_hides"),
                    (By.ID, "onetrust-accept-btn-handler"),  # OneTrust
                    (By.CSS_SELECTOR, ".cookie-banner .accept"),  # Generic cookie banner
                    (By.CSS_SELECTOR, "p.ot-dpd-desc + button")  # Other privacy dialogs
                ]
                
                for by, selector in overlay_selectors:
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((by, selector))).click()
                        print(f"Dismissed overlay with selector: {selector}")
                        break
                    except:
                        continue
            except Exception as e:
                print(f"Overlay handling attempt: {str(e)}")

            # Login form interaction
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'email'))
            )
            email_field.clear()
            email_field.send_keys('youremail@gmail.com')  # Replace with your email
            print('Email inserted')
            
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'password'))
            )
            password_field.clear()
            password_field.send_keys('supersecurepassword')  # Replace with your password
            print('Password inserted')

            # Handle submit button with multiple approaches
            submit_button_locator = (By.CSS_SELECTOR, 'button[type="submit"].button--primary')
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(submit_button_locator)
            )
            
            try:
                # First try regular click
                submit_button.click()
                print('Submit button clicked normally')
            except:
                # Fallback to JavaScript click
                driver.execute_script("arguments[0].click();", submit_button)
                print('Submit button clicked via JavaScript')

            # Wait for successful login confirmation
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: 'Almost done' in d.page_source or 
                            'Welcome' in d.page_source or
                            'Dashboard' in d.page_source
                )
                self.logger.info("✅ Login successful!")
                
                # Process each listing form
                for row in rows:
                    self.logger.info(f"Processing form for listing: {row['Title']}\n")
                    self.logger.info(f"Processing form for listing: {row['Form_link']}")
                    
                    # Create the SeleniumRequest
                    request = SeleniumRequest(
                        url=row['Form_link'],
                        callback=self.handle_form_submission,
                        meta={
                            'driver': driver,
                            'row': row  # Pass both driver and row data
                        },
                        dont_filter=True
                    )
                    
                    # Yield the request and wait for it to complete
                    yield request
                    
                    # Add a 10-second delay before the next request
                    self.logger.info("Waiting for 10 seconds before the next request...")
                    time.sleep(10)

            except TimeoutException:
                # Check if login actually failed
                if "invalid credentials" in driver.page_source.lower():
                    self.logger.error("❌ Login failed: Invalid credentials")
                else:
                    self.logger.error("❌ Login confirmation timeout")
                driver.save_screenshot('login_error.png')
                raise

        except Exception as e:
            self.logger.error(f"❌ Login process failed: {str(e)}")
            driver.save_screenshot('login_error.png')
            raise
    def handle_form_submission(self, response):
        """Handle form interaction and submission"""

        driver = response.request.meta['driver']
        row = response.request.meta['row']
        motivation_template_file = 'Your_Motivation_Template.txt' # Ensure the template file exists

        try:
            with open(motivation_template_file, 'r') as f:
                motivation_template = f.read()

            row_data = {k: ("" if v is None else v) for k, v in row.items()}
            motivation_text = motivation_template.format(**row_data)

            # Fill the motivation textarea
            textarea = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.NAME, 'contact_agent_huurprofiel_form[motivation]')
                )
            )
            textarea.clear()  # Clear existing text
            textarea.send_keys(motivation_text)  # Add new text

            # Verify the text was added 
            if "Beginning of your motivation text;" in textarea.get_attribute('value'): # Adjust this condition based on your template
                self.logger.info("✅ Motivation text was added successfully!")
            else:
                self.logger.error("❌ Motivation text was not added.")
                return
    	    
            # Verify salutation (selected="selected">Sir</option>)
            salutation_select = driver.find_element(By.NAME, 'contact_agent_huurprofiel_form[salutation]')
            selected_option = salutation_select.find_element(By.CSS_SELECTOR, 'option[selected="selected"]')
            if selected_option.text.strip() == 'Select_Gender': # Adjust this based on your form
                self.logger.info("✅ Salutation is correctly set to 'Select_Gender'")
            else:
                self.logger.error(f"❌ Salutation is not set to 'Sir'. Found: {selected_option.text}")
                return

            # Verify first name (value='XXXXXX')
            first_name_input = driver.find_element(By.NAME, 'contact_agent_huurprofiel_form[first_name]')
            if first_name_input.get_attribute('value') == 'MY_FIRST_NAME': # Adjust this based on your form
                self.logger.info("✅ First name is correctly set to 'MY_FIRST_NAME'")
            else:
                self.logger.error(f"❌ First name is not set to 'MY_FIRST_NAME'. Found: {first_name_input.get_attribute('value')}")
                return

            # Verify last name (value='XXXXXXX')
            last_name_input = driver.find_element(By.NAME, 'contact_agent_huurprofiel_form[last_name]')
            if last_name_input.get_attribute('value') == 'My_Last_Name': # Adjust this based on your form
                self.logger.info("✅ Last name is correctly set to 'My_Last_Name'")
            else:
                self.logger.error(f"❌ Last name is not set to 'My_Last_Name'. Found: {last_name_input.get_attribute('value')}")
                return

            # Verify phone number (value='9999999')
            phone_number_input = driver.find_element(By.NAME, 'contact_agent_huurprofiel_form[phone_number]')
            if phone_number_input.get_attribute('value') == '9999999': # Adjust this based on your form
                self.logger.info("✅ Phone number is correctly set to '9999999'")
            else:
                self.logger.error(f"❌ Phone number is not set to '9999999'. Found: {phone_number_input.get_attribute('value')}")
                return

            # Verify date of birth (value='AAAA-BB-CC')
            date_of_birth_input = driver.find_element(By.NAME, 'contact_agent_huurprofiel_form[date_of_birth]')
            if date_of_birth_input.get_attribute('value') == 'AAAA-BB-CC': # Adjust this based on your form
                self.logger.info("✅ Date of birth is correctly set to 'AAAA-BB-CC'")
            else:
                self.logger.error(f"❌ Date of birth is not set to 'AAAA-BB-CC'. Found: {date_of_birth_input.get_attribute('value')}")
                return
            

            submit_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button.form__button--submit.form__button--submit-normal')
                )
            )

            
            if not submit_button.is_displayed():
                self.logger.warning("Submit button not visible")
                return
                
            if not submit_button.is_enabled():
                self.logger.warning("Submit button disabled - check form validation")
                return

            
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Allow for scroll completion
            submit_button.click()
            self.logger.info(f"Form submitted for: {row['Title']}, be alert final check is incoming!!")

            
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[contains(text(), "Your request has been sent")]')
                )
            )
            self.logger.info("Submission confirmation received")

        except TimeoutException:
            self.logger.error("Submission confirmation timeout")
            driver.save_screenshot("submission_timeout.png")
        except Exception as e:
            self.logger.error(f"Submission failed: {str(e)}")
            driver.save_screenshot("submission_error.png")
        finally:
            # 6. Reset browser state
            driver.refresh()  # Refresh the current page
            time.sleep(3)  # Cleanup pause

            # Store successful submission
            self.processed_rows.append(row['Title'])
            self.logger.info(f"Submitted form for listing {row['Title']}")

    def closed(self, reason):
        """Final cleanup"""
        self.logger.info(f"Successfully processed {len(self.processed_rows)} listings")