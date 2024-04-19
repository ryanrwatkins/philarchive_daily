import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

gmail_pw = os.environ["SECRET_GMAIL_PW"]
gmail_address = os.environ["SECRET_GMAIL"]
email_address = os.environ["SECRET_EMAIL"]
rss_url = os.environ["SECRET_RSS"]

# Calculate yesterday's date in the format used by the website (adjust format as needed)
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# URL of the website to scrape
url = 'https://philarchive.org/#selecteditems'

# Send a GET request to the website
response = requests.get(url)
response.raise_for_status()  # Raise an error if the request was unsuccessful

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Find the first <div id="entries"> element
entries_div = soup.find('div', id='entries')

# Initialize an empty string to hold the formatted results
results_str = ""

# Iterate through each <li class="entry"> within the <div id="entries">
for entry in entries_div.find_all('li', class_='entry'):
    # Check if the entry has yesterday's date
    date_div = entry.find('div', class_="subtle", style="float:right")
    if date_div and date_div.text.strip() == yesterday:
        # Find the citation span
        citation_span = entry.find('span', class_="citation")
        if citation_span:
                    # Extract the first <a> tag within the citation span for title and link
          title_link_a = entry.find('span', class_="citation").find('a', href=True)
          if title_link_a:
              title = title_link_a.text.strip()
              link = title_link_a['href']
              # Ensure the link is a complete URL
              if not link.startswith('http'):
                  link = f"https://philarchive.org{link}"
              # Format title with link in bold and as a header
              results_str += f"<h2><b><a href='{link}'>{title}</a></b></h2>\n"
          
            
          # Extract the abstract
          abstract_div = entry.find('div', class_="abstract")
          if abstract_div:
              abstract = abstract_div.text.strip()
              # Append the abstract to the results string
              results_str += f"<p>{abstract}</p>\n"
          
          # Add a space before the next entry
          results_str += "<br>\n"




#this will email the resulting "todays_articles"
import smtplib
from email.mime.text import MIMEText

# Set Global Variables
gmail_user = gmail_address 
gmail_password = gmail_pw

# this is an app password not your personal password, instructions for setting this up are found at: support.google.com/accounts/answer/185833?hl=en

# to and from
mail_from = gmail_user
mail_to = [rss_url, email_address]  #the first email address creates an RSS feed using https://kill-the-newsletter.com/

# create message
msg = MIMEText(results_str, 'html') 
msg['Subject'] = 'PhilArchive articles for ' + yesterday
msg['From'] = mail_from
msg['To'] = ", ".join(mail_to)   #this allows for multiple recipients

# Send
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(gmail_user, gmail_password)
server.sendmail(mail_from, mail_to, msg.as_string())
server.close()
