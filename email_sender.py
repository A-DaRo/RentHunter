from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
import pandas as pd

def get_attachments_from_directory(directory):
    """Get all files in a directory as attachments."""
    attachments = []
    if os.path.exists(directory) and os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                attachments.append(file_path)
    return attachments

def create_message(subject, body, attachments=None, cc=None):
    """Create email message with text, attachments, and CC."""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Add CC recipients if provided
    if cc:
        msg['Cc'] = ', '.join(cc)
    
    # Add attachments if provided
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
            except Exception as e:
                print(f"Failed to attach {file_path}: {str(e)}")
    return msg

def send_listing_email(row, config, debug=False, pararius=False):
    """Send email for a property listing using a configuration dictionary."""
    smtp_server = config['server']
    smtp_port = config['port']
    sender_email = config['sender_email']
    sender_password = config['password']
    default_receiver = config['default_receiver']
    body_template_file = config['body_template_file']
    attachment_directory = config['attachment_directory']
    cc = config['cc']

    # Determine receiver email and message content
    receiver_email = row.get('Agency_Email')
    use_default = False

    if debug==True:
        print('DEBUG MODE IS ON, sending to default receiver')
        use_default = True
        receiver_email = default_receiver
        subject = 'NEW LISTING FOUND IN DEBUG MODE'
        body_template = """New property listing from {Agency_Name}!

Title: {Title}
Price: €{Rent_Price}
Surface: {Living_Area} m²
Rooms: {Number_of_Rooms}

Check full details: {URL}"""
            
    else:
        if pararius==False:
            print('FRESH LISTING APPEARED OUTSIDE OF PARARIUS, sending to default receiver')
            use_default = True
            receiver_email = default_receiver
            subject = 'FRESH LISTING OUTSIDE OF PARARIUS'
            body_template = """New property listing from {Agency_Name}!

Title: {Title}
Price: €{Rent_Price}
Surface: {Living_Area} m²
Rooms: {Number_of_Rooms}

Check full details: {URL}"""

        elif pd.isna(receiver_email) or not receiver_email:
            print('ATTENTION: Impossible to determine receiver mail, falling back to default_receiver')
            use_default = True
            receiver_email = default_receiver
            subject = 'NEW LISTING WITHOUT EMAIL'
            body_template = """New property listing from {Agency_Name}!

Title: {Title}
Price: €{Rent_Price}
Surface: {Living_Area} m²
Rooms: {Number_of_Rooms}

Check full details: {URL}"""

        else:
            subject = f"Interest in the rental offer: {row.get('Title', 'No Title')}"
            with open(body_template_file, 'r') as f:
                body_template = f.read()


    # Replace None values with empty strings in the row data
    row_data = {k: ("" if v is None else v) for k, v in row.to_dict().items()}
    body = body_template.format(**row_data)

    # Get attachments from the directory
    attachments = []
    if attachment_directory and use_default==False:
        attachments = get_attachments_from_directory(attachment_directory)
        if not attachments:
            print(f"No attachments found in directory: {attachment_directory}")

    # Create and send message
    msg = create_message(subject, body, attachments, cc)
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Combine receiver and CC emails for sendmail
            all_recipients = [receiver_email]
            if cc:
                all_recipients.extend(cc)
            
            server.sendmail(from_addr=sender_email, to_addrs=all_recipients, msg=msg.as_string())
        print(f"Email sent to {receiver_email} with CC: {cc if cc else 'None'}")
        if attachments:
            print(f"Attachments: {', '.join(os.path.basename(f) for f in attachments)}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Configuration
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'sender_email': 'sender_email@gmail.com', # Replace with your email
    'password': 'AAAA BBBB CCCC DDDD', # Replace with your app password
    'default_receiver': 'your_personal@email.com', # Replace with your personal email
    'body_template_file': 'Your_Housing_Email_Template.txt', # Ensure the template file exists
    'attachment_directory': r"Your_Attachements",  # Directory containing attachments
    'cc': ['my.friend@email.com', 'my.parent@email.com']  # Add CC recipients here
}