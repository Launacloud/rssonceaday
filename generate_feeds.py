import os
from urllib.parse import urljoin
from datetime import datetime
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from pytz import timezone
import json

feeds = [
    {
        "title": "Palavra do Dia RSS",
        "subtitle": "Daily words from Dicio",
        "url": "https://www.dicio.com.br/palavra-do-dia/",
        "author_name": "Dicio",
        "author_email": "contact@dicio.com.br",
        "copyright": "Dicio",
        "language": "pt",
        "item_title_css": ".word-of-day .title",
        "item_url_css": ".word-of-day .title a",
        "item_author_css": None,
        "item_description_css": ".word-of-day--text-wrap .word-of-day--description",
        "item_date_css": ".word-of-day .title",
        "item_date_format": "%d/%m/%Y",
        "item_timezone": "America/Sao_Paulo",
        "output_path": "feeds/palavra_do_dia",
        "formats": ["xml", "json"]
    }
]

def generate_feed(feed_config):
    r = requests.get(feed_config["url"])
    soup = BeautifulSoup(r.text, 'html.parser')

    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
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

for feed in feeds:
    generate_feed(feed)
