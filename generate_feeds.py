import os
from urllib.parse import urljoin
from datetime import datetime
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from pytz import timezone

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
    soup = BeautifulSoup(r.text, 'lxml')

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

    for i in range(len(titles)):
        fe = fg.add_entry()
        fe.title(titles[i].text)
        item_url = urljoin(feed_config["url"], urls[i].get('href'))
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        if descriptions:
            fe.description(descriptions[i].text)

        if authors:
            fe.author(name=authors[i].text)

        if dates:
            date = datetime.strptime(dates[i].text.strip(), feed_config["item_date_format"])
            localtz = timezone(feed_config["item_timezone"])
            date = localtz.localize(date)
            fe.published(date)
            fe.updated(date)

    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)

    if "xml" in feed_config["formats"]:
        fg.atom_file(os.path.join(output_path, 'atom.xml'))

    if "json" in feed_config["formats"]:
        fg.json_file(os.path.join(output_path, 'feed.json'))

for feed in feeds:
    generate_feed(feed)
