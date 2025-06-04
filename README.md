# RentHunter: Automated Housing Listing Scraper & Email Notifier

**RentHunter** was initially developed with the specific goal of finding student rental offers in the vibrant city of Eindhoven, The Netherlands. However, its underlying architecture and scraping logic are designed to be highly adaptable. With minor modifications, such as changing the `start_urls` variable within each spider's class definition (and potentially adjusting location-specific filters), RentHunter can be easily generalized to search for rental properties across the entire country or even other regions with similar housing portal structures.

**Disclaimer:** This repository is for educational and informational purposes only. The code and techniques demonstrated should not be used for any commercial or business intent unless in strict accordance with all applicable laws and regulations, including but not limited to the European General Data Protection Regulation (GDPR) and the terms of service of the websites being scraped. Always respect website terms of service and robots.txt files.

## Table of Contents

1.  [Features](#features)
2.  [Why VPN/Proxies are Essential](#why-vpnproxies-are-essential)
3.  [Prerequisites](#prerequisites)
4.  [Setup Instructions](#setup-instructions)
    *   [Clone the Repository](#clone-the-repository)
    *   [Create Conda Environment](#create-conda-environment)
    *   [Install Dependencies](#install-dependencies)
    *   [Mullvad VPN Setup](#mullvad-vpn-setup)
5.  [Configuration](#configuration)
    *   [Email Sender Configuration (`email_sender.py`)](#email-sender-configuration-email_senderpy)
    *   [Email Body Template (`Your_Housing_Email_Template.txt`)](#email-body-template-your_housing_email_templatetxt)
    *   [Email Attachments (`Your_Attachements/`)](#email-attachments-your_attachements)
    *   [Pararius Login Spider Configuration (`par_login.py`)](#pararius-login-spider-configuration-par_loginpy)
    *   [Adapting Spiders for Different Locations](#adapting-spiders-for-different-locations)
6.  [File Descriptions](#file-descriptions)
7.  [Running the Pipeline](#running-the-pipeline)
8.  [How it Works](#how-it-works)
9.  [Contribution & Future Work](#contribution--future-work)

## Features

*   Scrapes multiple housing websites (Pararius, Friendly Housing, Rotsvast, Hunting, Extate, Lightcity).
*   Detects new listings by comparing against previously scraped data.
*   Filters new listings based on predefined criteria.
*   Sends email notifications for relevant new listings.
*   Automated IP rotation using Mullvad VPN to prevent blocking and enhance privacy.
*   Conditional email sending logic (e.g., different recipients/subjects for debug mode, Pararius listings, or listings without agency emails).
*   Automated form submission on Pararius for listings that meet criteria (via `par_login.py`).
*   Scheduled execution with different frequencies for day and night.
*   Debug mode for testing.

## Why VPN/Proxies are Essential

When scraping websites frequently, your IP address can be flagged and blocked by the target sites if they detect unusual activity. This can halt your scraping operations. Furthermore, exposing your personal IP address while scraping can compromise your online privacy.

**Benefits of using a VPN or Proxy Service:**

1.  **IP Rotation:** By routing your traffic through different servers, you change your apparent IP address. This makes it harder for websites to identify and block your scraper.
2.  **Privacy Protection:** Your real IP address is masked, protecting your identity and location.
3.  **Bypassing Geo-restrictions:** Some websites show different content or restrict access based on geographic location. A VPN allows you to appear as if you're browsing from a different region.

**Mullvad VPN:**
This project uses Mullvad VPN. Mullvad is an excellent choice for several reasons:
*   **Strong Privacy Focus:** They have a strict no-logging policy and prioritize user anonymity.
*   **Command-Line Interface (CLI):** The `mullvad` CLI allows for programmatic control of VPN connections, which is essential for this pipeline to automatically change server locations.
*   **Good Performance:** Generally offers reliable speeds and a wide range of server locations.
*   **Transparent Pricing:** Simple, flat-rate pricing.

**Other Recommendations:**
*   **ProtonVPN:** Another reputable VPN provider with a strong focus on privacy and security. They also offer a CLI.
*   **Commercial Proxy Providers:** Services like Bright Data, Oxylabs, or Smartproxy offer vast pools of residential or datacenter proxies. These are often more expensive but can provide more granular control and a larger IP pool.

**Important Note:** Reliable VPN and proxy services are typically paid services. While free options exist, they often come with limitations, security risks, or poor performance, making them unsuitable for serious scraping tasks.

## Prerequisites

*   Python 3.8+
*   Conda (Miniconda or Anaconda)
*   Git
*   Mullvad VPN account and the Mullvad VPN command-line interface (CLI) installed and configured.
*   An email account (e.g., Gmail) to be used for sending notifications. If using Gmail, you'll need to set up an "App Password".
*   A Pararius account (if you intend to use the `par_login.py` spider for automated form submissions).
*   Google Chrome browser installed (as `par_login.py` uses Selenium with ChromeDriver).

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/A-DaRo/RentHunter
cd RentHunter
```

### 2. Create Conda Environment
Create a dedicated Conda environment for this project:
```bash
conda create -n renthunter_env python=3.9
conda activate renthunter_env
```
(You can replace `renthunter_env` with your preferred environment name and `3.9` with a desired Python 3 version).

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
**Note:** You will also need a `chromedriver` compatible with your Chrome version (and, of course, chrome installed). `scrapy-selenium` often attempts to download a compatible `chromedriver`, but manual installation (ensuring it's in your system's PATH) might be necessary.

### 4. Mullvad VPN Setup
1.  Ensure you have a Mullvad VPN account.
2.  Install the Mullvad VPN application and its command-line interface (CLI).
    *   On Linux, the CLI is usually installed with the app.
    *   On macOS, you might need to create a symlink: `sudo ln -s /Applications/Mullvad\ VPN.app/Contents/Resources/mullvad-daemon /usr/local/bin/mullvad`
    *   On Windows, ensure the Mullvad installation directory (containing `mullvad.exe`) is in your system's PATH.
3.  Log in to your Mullvad account via the CLI or GUI. The script assumes you are already logged in.
    ```bash
    mullvad account login <YOUR_MULLVAD_ACCOUNT_NUMBER>
    ```

## Configuration

Several parts of the pipeline need to be configured with your specific details.

### 1. Email Sender Configuration (`email_sender.py`)
Open `email_sender.py` and modify the `SMTP_CONFIG` dictionary:

```python
# email_sender.py

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',  # SMTP server (e.g., 'smtp.gmail.com' for Gmail)
    'port': 587,                 # SMTP port (587 for TLS, 465 for SSL)
    'sender_email': 'your_sender_email@gmail.com', # Your email address
    'password': 'YOUR_GMAIL_APP_PASSWORD', # Your email app password (NOT your regular password)
    'default_receiver': 'your_personal_email@example.com', # Email for debug/fallback
    'body_template_file': 'Your_Housing_Email_Template.txt', # Path to email body template
    'attachment_directory': r"Your_Attachements",  # Path to directory with attachments
    'cc': ['friend1@example.com', 'family_member@example.com']  # List of CC recipients
}
```
*   **`sender_email`**: The email address from which notifications will be sent.
*   **`password`**: If using Gmail, generate an "App Password" (Google "Gmail App Password" for instructions) and use that here. Do not use your main Gmail password.
*   **`default_receiver`**: Your personal email address where debug messages or listings without agency contact info will be sent.
*   **`body_template_file`**: The name of the text file containing the email body template for initial contact.
*   **`attachment_directory`**: The name of the directory where your attachment files (e.g., cover letter, proof of income) are stored for the initial email.
*   **`cc`**: A list of email addresses to be CC'd on the emails.

### 2. Email Body Template (`Your_Housing_Email_Template.txt`)
Create a file named `Your_Housing_Email_Template.txt` (or the name you specified in `SMTP_CONFIG`) in the root directory of the project. This file will contain the template for the email body sent to agencies for general listings.
Example `Your_Housing_Email_Template.txt`:
```txt
Dear {Agency_Name},

I am writing to express my strong interest in the property located at {Title}, which I found listed with a rent of €{Rent_Price} per month and a living area of {Living_Area} m².

[Your standard introduction - e.g., about yourself, your employment, why you're looking for a place]

I have attached my [mention your attachments, e.g., proof of income and a cover letter] for your review.
I am available for viewings at your earliest convenience and can be reached at [Your Phone Number] or via this email address.

Thank you for your time and consideration.

Sincerely,
[Your Name]
```
The placeholders like `{Title}`, `{Agency_Name}`, `{Rent_Price}` etc., will be automatically filled by the script using data from the scraped listing.

### 3. Email Attachments (`Your_Attachements/`)
Create a directory named `Your_Attachements` (or the name you specified in `SMTP_CONFIG`) in the root directory. Place any files you want to attach to the initial contact emails (e.g., a PDF of your cover letter, proof of income) into this directory.

### 4. Pararius Login Spider Configuration (`par_login.py`)

If you intend to use the `par_login.py` spider for automatically submitting interest forms on Pararius, you need to configure it:

**a. Login Credentials:**
Open `par_login.py` and update the following lines within the `handle_login` method:
```python
# par_login.py -> handle_login method
email_field.send_keys('youremail@gmail.com')  # Replace with your Pararius login email
# ...
password_field.send_keys('supersecurepassword')  # Replace with your Pararius password
```

**b. Motivation Text Template:**
Create a file named `Your_Motivation_Template.txt` in the root directory. This template will be used to fill the "motivation" or "message" field in the Pararius contact form.
Example `Your_Motivation_Template.txt`:
```txt
Beginning of your motivation text;

Dear Sir/Madam,

I am very interested in the property: {Title} located at {Street}.
My current situation is [briefly explain your situation, e.g., "I am a young professional looking for a long-term rental"].
I am looking for a [apartment/house] with {Number_of_Rooms} rooms and approximately {Living_Area} m².
The advertised price of €{Rent_Price} is within my budget.

[Add more details about yourself, your work, household composition, etc., as you see fit for a motivation letter]

I would appreciate the opportunity to schedule a viewing.

Thank you,
[Your Full Name]
[Your Phone Number]
[Your Email Address]
```
The placeholders like `{Title}`, `{Street}`, `{Number_of_Rooms}` will be filled from the listing data. The `par_login.py` script currently checks if `"Beginning of your motivation text;"` is present in the textarea after filling it. Adjust this check in `handle_form_submission` if you change your template significantly.

**c. Pre-filled Form Value Verification:**
The `par_login.py` spider attempts to verify that certain fields in your Pararius profile (which are pre-filled in the contact form) match expected values. You **MUST** update these expected values in the `handle_form_submission` method of `par_login.py` to match your actual Pararius profile information. If these don't match, the form submission might be skipped for that listing.

Locate and update these lines in `par_login.py` (`handle_form_submission` method):
```python
# par_login.py -> handle_form_submission method

# Verify salutation
if selected_option.text.strip() == 'Select_Gender': # Adjust 'Select_Gender' to your actual salutation (e.g., 'Sir', 'Madam')
    self.logger.info("✅ Salutation is correctly set")
# ... (rest of the verification blocks)
```
**Important:** Ensure these values exactly match what Pararius pre-fills from your profile.

### 5. Adapting Spiders for Different Locations
As mentioned, RentHunter was initially set for Eindhoven. To target other cities or regions:
*   **Locate Spiders:** The individual Scrapy spiders (e.g., `pararius.py`, `friendlyhousing.py`, etc. - these would typically be in a `spiders` sub-directory of a Scrapy project) will have a variable that defines the starting URL or search query. This is often `start_urls` and a custom variable like `refined_selection` used to construct the `start_urls`.
*   **Modify `refined_selection` / `start_urls`:**
    *   For example, in a hypothetical `pararius_spider.py`, you might find:
      ```python
      class ParariusSpider(scrapy.Spider):
          name = "pararius"
          refined_selection = "eindhoven" # Modify this
          start_urls = [f"https://www.pararius.com/english/{refined_selection}"]
          # ... rest of the spider
      ```
      Change `"eindhoven"` to your desired city (e.g., `"amsterdam"`, `"utrecht"`). The exact URL structure will depend on the target website.
*   **Adjust Filters:** The filtering logic (likely in `pd_helpers.py` and used in `email_pipeline.py`) might also need adjustment if your criteria change based on location (e.g., price ranges).

## File Descriptions

*   **`run_email_pipeline.py`**: Main entry point, manages VPN and schedules `email_pipeline.py`.
*   **`email_pipeline.py`**: Core scraping logic, runs spiders, processes data, triggers notifications/form submissions.
*   **`email_sender.py`**: Handles sending general email notifications.
*   **`par_login.py`**: Scrapy spider for logging into Pararius and submitting contact forms.
*   **`pd_helpers.py`** (Assumed): Contains Pandas helper functions for data cleaning and filtering.
*   **`Your_Housing_Email_Template.txt`**: Template for general emails to agencies.
*   **`Your_Motivation_Template.txt`**: Template for Pararius contact form motivation.
*   **`Your_Attachements/`**: Directory for email attachments.
*   **`*_listings.csv` / `*_listings.json`**: Data storage for scraped listings.
*   **`requirements.txt`**: Project dependencies.
*   **(Spiders Directory - e.g., `renthunter/spiders/`)** (Assumed for a standard Scrapy project): This directory would contain the individual Python files for each website spider (e.g., `pararius_spider.py`, `friendlyhousing_spider.py`). These are the files you'd modify to change target locations.

## Running the Pipeline

1.  Ensure your Conda environment is activated:
    ```bash
    conda activate renthunter_env
    ```
2.  Navigate to the project's root directory.
3.  Verify Mullvad VPN, email, Pararius, and template configurations.
4.  Run:
    ```bash
    python run_email_pipeline.py
    ```
5.  For debug mode:
    ```bash
    python run_email_pipeline.py --debug
    ```

## How it Works

1.  **VPN Connection (`run_email_pipeline.py`)**: Connects via Mullvad.
2.  **Scheduling (`run_email_pipeline.py`)**: Calls `email_pipeline.py` at set intervals.
3.  **Scraping & Processing (`email_pipeline.py`)**: Loads old data, runs spiders (from your `spiders` directory, configured for a target location), gets new data, compares, cleans, filters.
4.  **Notification/Action Logic (`email_pipeline.py`)**:
    *   **Pararius:** Triggers `par_login.py` for new, filtered Pararius listings to auto-submit forms.
    *   **Others:** Sends emails via `email_sender.py` for other new, filtered listings.
5.  **Loop**: Repeats.

## Contribution & Future Work

The spiders and automation scripts provided in this repository are functional but can always be improved. Web scraping is a dynamic field, and website structures change.

*   **Contributions Welcome:** Forks and pull requests are highly encouraged! If you improve a spider, enhance error handling, add new features, or fix bugs, please consider contributing back.
*   **Cite this Work:** If your work builds upon or is inspired by this project, please provide appropriate citation or a link back to this repository.
*   **Potential Improvements:**
    *   More robust error handling and retry mechanisms for spiders.
    *   Advanced anti-scraping bypass techniques (though always use ethically).
    *   Dynamic configuration for spider settings.
    *   A web interface for managing the pipeline.
    *   More sophisticated filtering criteria.
    *   Support for more housing websites.

This project aims to be a helpful starting point for anyone looking to automate their housing search or learn about web scraping and automation techniques.
```