import subprocess
import time
from datetime import datetime, time as dt_time
import argparse
import random


M_connect = {
    "al": ["tia"],
    "au": ["adl", "bne", "mel", "per", "syd"],
    "at": ["vie"],
    "be": ["bru"],
    "br": ["sao"],
    "bg": ["sof"],
    "ca": ["yyc", "mtr", "tor", "van"],
    "cl": ["scl"],
    "co": ["bog"],
    "hr": ["zag"],
    "cy": ["nic"],
    "cz": ["prg"],
    "dk": ["cph"],
    "ee": ["tll"],
    "fi": ["hel"],
    "fr": ["bod", "mrs", "par"],
    "de": ["ber", "dus", "fra"],
    "gr": ["ath"],
    "hk": ["hkg"],
    "hu": ["bud"],
    "id": ["jpu"],
    "ie": ["dub"],
    "il": ["tlv"],
    "it": ["mil", "pmo"],
    "jp": ["osa", "tyo"],
    "my": ["kul"],
    "mx": ["qro"],
    "nl": ["ams"],
    "nz": ["akl"],
    "ng": ["los"],
    "no": ["osl", "svg"],
    "pe": ["lim"],
    "ph": ["mnl"],
    "pl": ["waw"],
    "pt": ["lis"],
    "ro": ["buh"],
    "rs": ["beg"],
    "sg": ["sin"],
    "sk": ["bts"],
    "si": ["lju"],
    "za": ["jnb"],
    "es": ["bcn", "mad", "vlc"],
    "se": ["got", "mma", "sto"],
    "ch": ["zrh"],
    "th": ["bkk"],
    "tr": ["ist"],
    "gb": ["glw", "lon", "mnc"],
    "ua": ["iev"],
    "us": ["qas", "atl", "bos", "chi", "dal", "den", "det", "hou", "lax", "txc", "mia", "nyc", "phx", "rag", "slc", "sjc", "sea", "uyk", "was"]
}

# Function to generate the first script dynamically
def generate_script1():
    # Randomly select a key from the dictionary
    s_code = random.choice(list(M_connect.keys()))
    # Randomly select a value from the list corresponding to the selected key
    c_code = random.choice(M_connect[s_code])
    # Generate the script as a string
    script1 = f"mullvad relay set location {s_code} {c_code}"
    return script1

# Function to generate the second script dynamically
def generate_script2():
    # Generate the script as a string
    script2 = "mullvad connect"
    return script2

# Function to run the dynamically generated scripts
def run_dynamic_scripts():

    print("Generating and running dynamic scripts... \n")
    
    # Generate script1
    script1 = generate_script1()
    print(f"Running script1: {script1} \n")
    subprocess.run(script1, shell=True, check=True)
    
    # Generate script2
    script2 = generate_script2()
    print(f"Running script2: {script2} \n")
    subprocess.run(script2, shell=True, check=True)
    
    print("Dynamic scripts completed. \n")

# Function to call email_pipeline.py
def call_email_pipeline(debug_mode):
    print("Calling email_pipeline.py... \n")
    if debug_mode:
        subprocess.run(["python", "email_pipeline.py", "--debug"], check=True)
    else:
        subprocess.run(["python", "email_pipeline.py"], check=True)
    print("email_pipeline.py completed. \n")

# Function to determine if the current time is within the specified range
def is_time_between(start_time, end_time):
    now = datetime.now().time()
    return start_time <= now <= end_time

# Function to run a bash script until 'Connected' is found in its output
def run_until_connected():

    print("Waiting for 'Connected' in the script output...")

    attempt_count = 0  # Initialize the attempt counter
    
    while True:
        # Run the bash script and capture its output
        result = subprocess.run('mullvad status', capture_output=True, text=True, shell=True, check=True)

        # Check if 'Connected' is in the output
        if "Connected" in result.stdout:
            print("'Connected' found in the output. Proceeding to the next step.")
            break

                # Increment the attempt counter
        attempt_count += 1
        print(f"'Connected' not found. Attempt {attempt_count} of 4.")

        # If 4 attempts have been made, rerun dynamic scripts and reset the counter
        if attempt_count >= 4:
            print("Maximum attempts reached. Rerunning dynamic scripts...")
            run_dynamic_scripts()
            attempt_count = 0  # Reset the counter

        # Wait for a short time before running the script again
        print("Retrying in 5 seconds...")
        time.sleep(5)

# Main function
def main(debug_mode):
    while True:
        # Run dynamic scripts
        run_dynamic_scripts()

        # Wait until 'Connected' is found in the output
        run_until_connected()

        # Call email_pipeline.py based on the time of day
        if is_time_between(dt_time(8, 0), dt_time(18, 0)):
            print("Running email_pipeline.py every 5 minutes (8 AM - 6 PM)... \n")
            call_email_pipeline(debug_mode)
            time.sleep(300)  # 5 minutes
        else:
            print("Running email_pipeline.py every 15 minutes (other hours)... \n")
            call_email_pipeline(debug_mode)
            time.sleep(900)  # 15 minutes

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run email_pipeline.py with optional debug mode.")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Start the main loop
    main(args.debug)