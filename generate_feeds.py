import os
import json
from datetime import datetime
from urllib.parse import urljoin
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
from pytz import timezone
import locale  # Import locale for setting date locale

# Import the feeds list from feed.py
from feed import feeds

# Function to set locale for date parsing
def set_locale():
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        print("Locale not available. Trying 'pt_PT.UTF-8'.")
        try:
            locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
        except locale.Error:
            print("Locale 'pt_PT.UTF-8' also not available. Please ensure locale is installed.")

# Function to generate feed
def generate_feed(feed_config):
    r = requests.get(feed_config["url"])
    soup = BeautifulSoup(r.text, 'html.parser')

    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []
    dates = soup.select(feed_config["item_date_css"]) if feed_config["item_date_css"] else []
    extras = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []  # Select first extra field
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []  # Select second extra field

    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    min_len = min(len(titles), len(urls) or len(titles), len(descriptions) or len(titles), len(authors) or len(titles), len(dates) or len(titles), len(extras) or len(titles), len(extras2) or len(titles))

    output_data = []  # List to store entry data

    # Set locale for date parsing
    set_locale()

    for i in range(min_len):
        fe = fg.add_entry()
        fe.title(titles[i].text)
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        description_text = descriptions[i].text if i < len(descriptions) else "No description found"
        # Remove newline characters from the description text using BeautifulSoup
        description_text = BeautifulSoup(description_text, 'html.parser').text.strip()

        # Include extra information directly in the description field
        if extras:
            extra_text = extras[i].text if i < len(extras) else "No extra information found"
            description_text += f"\n\nExtra 1: {extra_text}"
        
        if extras2:
            extra2_text = extras2[i].text if i < len(extras2) else "No second extra information found"
            description_text += f"\n\nExtra 2: {extra2_text}"

        fe.description(description_text)

        if authors:
            author_text = authors[i].text if i < len(authors) else "No author found"
            fe.author(name=author_text)

        if dates:
            date_text = dates[i].text if i < len(dates) else "No date found"
            date_format = feed_config["item_date_format"]
            try:
                date_obj = datetime.strptime(date_text.split()[-1][1:-1], date_format)
                date_obj = timezone(feed_config["item_timezone"]).localize(date_obj)
                fe.published(date_obj.isoformat())
            except ValueError as e:
                print(f"Error parsing date: {e}")

        # Store entry data in output_data list
        entry_data = {
            "Title": titles[i].text,
            "ID": item_url,
            "Description": description_text
        }
        output_data.append(entry_data)

    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)

    # Generate Atom feed
    atom_file_path = os.path.join(output_path, 'atom.xml')
    fg.atom_file(atom_file_path)

    # Write output_data to JSON file with pretty formatting
    json_file_path = os.path.join(output_path, 'feed.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json
