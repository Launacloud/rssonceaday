import os
from urllib.parse import urljoin
from datetime import datetime
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from pytz import timezone
import json

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

    entries = []  # List to store entries

    for i in range(min_len):
        entry = {
            "title": titles[i].text,
            "id": urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"],
            "description": descriptions[i].text if i < len(descriptions) else "No description found"
        }
        entries.append(entry)
        
        # Print ID of the entry
        print(f"ID of entry {i+1}: {entry['id']}")

    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)

    # Generate JSON file
    json_file_path = os.path.join(output_path, 'feed.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(entries, json_file, indent=4)  # Check the syntax here

# Generate feeds for each item in the feeds list imported from feed.py
for feed_config in feeds:
    generate_feed(feed_config)
