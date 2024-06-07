import os
import json
import xml.etree.ElementTree as ET

# Import the feeds list from feed.py
from feed import feeds
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import requests
from pytz import timezone

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

    for i in range(min_len):
        fe = fg.add_entry()
        fe.title(titles[i].text)
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        description_text = descriptions[i].text if i < len(descriptions) else "No description found"
        
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

    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)

    # Generate Atom feed
    atom_file_path = os.path.join(output_path, 'atom.xml')
    fg.atom_file(atom_file_path)

    # Extract atom_feed from the generated XML file
    atom_feed = extract_atom_feed(atom_file_path)

    # Generate JSON feed by converting Atom feed
    if atom_feed:
        # Define JSON data structure
        json_data = {
            "Title of xml file": feed_config["title"],  # Title of XML file
            "ID": feed_config["url"],  # ID
            "Content": atom_feed,  # Content (Atom feed)
        }

        # Write JSON data to file
        json_file_path = os.path.join(output_path, 'feed.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)  # Indent for pretty formatting
        print(f"JSON file '{json_file_path}' created successfully.")
    else:
        print("Atom feed is empty.")

# Function to extract atom_feed from the generated XML file
def extract_atom_feed(atom_file_path):
    if os.path.exists(atom_file_path):
        with open(atom_file_path, 'r', encoding='utf-8') as atom_file:
            atom_feed = atom_file.read()
            return atom_feed
    else:
        print("Atom feed file not found.")
        return None

# Generate feeds for each item in the feeds list imported from feed.py
for feed_config in feeds:
    generate_feed(feed_config)
