# Import the feeds list from feed.py
from feed import feeds
import os
from urllib.parse import urljoin
from datetime import datetime
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from pytz import timezone
import json
import xml.etree.ElementTree as ET

# Function to generate feed
def generate_feed(feed_config):
    r = requests.get(feed_config["url"])
    soup = BeautifulSoup(r.text, 'html.parser')

    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    extras = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []  # Select first extra field
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []  # Select second extra field
    authors = soup.select(feed_config["item_author_css"]) if "item_author_css" in feed_config else []
    dates = soup.select(feed_config["item_date_css"]) if "item_date_css" in feed_config else []

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

        # Include extra information from item_extra_css and item_extra_css2
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

    # Generate JSON feed by converting Atom feed
    atom_str = fg.atom_str(pretty=True)
    if atom_str:
        atom_str_decoded = atom_str.decode("utf-8")  # Decode bytes to string
        feed_items = []

        root = ET.fromstring(atom_str_decoded)
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            item = {}
            item['Title'] = entry.find('{http://www.w3.org/2005/Atom}title').text
            item['ID'] = entry.find('{http://www.w3.org/2005/Atom}id').text
            item['Content'] = entry.find('{http://www.w3.org/2005/Atom}content').text.strip()
            feed_items.append(item)

        json_data = {
            "feed_items": feed_items
        }
        json_file_path = os.path.join(output_path, 'feed.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    else:
        print("Atom feed is empty.")

# Generate feeds for each item in the feeds list imported from feed.py
for feed_config in feeds:
    generate_feed(feed_config)
