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
    extras1 = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []  # Select first extra field
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []  # Select second extra field
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []
    dates = soup.select(feed_config["item_date_css"]) if feed_config["item_date_css"] else []

    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    min_len = min(len(titles), len(urls) or len(titles), len(descriptions) or len(titles), len(authors) or len(titles), len(dates) or len(titles))

    for i in range(min_len):
        fe = fg.add_entry()
        fe.title(titles[i].text)
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        if descriptions:
            description_text = descriptions[i].text if i < len(descriptions) else "No description found"
            fe.description(description_text)

        if extras1:
            extra_text1 = extras1[i].text if i < len(extras1) else ""
            fe.description(fe.description() + "\n" + extra_text1)
        
        if extras2:
            extra_text2 = extras2[i].text if i < len(extras2) else ""
            fe.description(fe.description() + "\n" + extra_text2)

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
    atom_str = fg.atom_str()
    if atom_str:
        atom_str_decoded = atom_str.decode("utf-8")  # Decode bytes to string
        json_data = {
            "atom_feed": atom_str_decoded,
            "config": feed_config
        }
        json_file_path = os.path.join(output_path, 'feed.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    else:
        print("Atom feed is empty.")

# Parse environment variables to create feed configurations
feeds = []
feed_prefixes = os.getenv('FEED_PREFIXES', '').split(',')

for prefix in feed_prefixes:
    if prefix:
        feeds.append({
            "title": os.getenv(f"{prefix}_TITLE"),
            "subtitle": os.getenv(f"{prefix}_SUBTITLE"),
            "url": os.getenv(f"{prefix}_URL"),
            "author_name": os.getenv(f"{prefix}_AUTHOR_NAME"),
            "author_email": os.getenv(f"{prefix}_AUTHOR_EMAIL"),
            "copyright": os.getenv(f"{prefix}_COPYRIGHT"),
            "language": os.getenv(f"{prefix}_LANGUAGE"),
            "item_title_css": os.getenv(f"{prefix}_ITEM_TITLE_CSS"),
            "item_url_css": os.getenv(f"{prefix}_ITEM_URL_CSS"),
            "item_author_css": os.getenv(f"{prefix}_ITEM_AUTHOR_CSS"),
            "item_description_css": os.getenv(f"{prefix}_ITEM_DESCRIPTION_CSS"),
            "item_extra_css": os.getenv(f"{prefix}_ITEM_EXTRA_CSS"),  # New extra field
            "item_extra_css2": os.getenv(f"{prefix}_ITEM_EXTRA_CSS2"),  # New extra field
            "item_date_css": os.getenv(f"{prefix}_ITEM_DATE_CSS"),
            "item_date_format": os.getenv(f"{prefix}_ITEM_DATE_FORMAT"),
            "item_timezone": os.getenv(f"{prefix}_ITEM_TIMEZONE"),
            "output_path": os.getenv(f"{prefix}_OUTPUT_PATH"),
            "formats": os.getenv(f"{prefix}_FORMATS", "xml,json").split(',')
        })

# Generate feeds for each item in the feeds list
for feed in feeds:
    generate_feed(feed)
