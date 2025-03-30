import os
import json
import hashlib
import requests
import sys
import logging
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import feedparser

try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    logging.warning("Warning: 'gitpython' module not found. Git change reporting will be skipped.")

from feed import feeds

should_print_last_entries = True

# Setup logging
logging.basicConfig(filename='output.log', level=logging.INFO, filemode='w')
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)

def generate_entry_id(title):
    unique_string = title.strip()
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def generate_feed(feed_config, should_print_last_entries=False):
    atom_file_path = os.path.join(feed_config["output_path"], 'atom.xml')
    json_file_path = os.path.join(feed_config["output_path"], 'feed.json')

    logging.info(f"Checking files: atom.xml exists={os.path.exists(atom_file_path)}, feed.json exists={os.path.exists(json_file_path)}")

    try:
        r = requests.get(feed_config["url"])
        logging.info(f"Fetching {feed_config['url']} - Status Code: {r.status_code}")
        logging.info(f"Response length: {len(r.text)} characters")
    except requests.RequestException as e:
        logging.error(f"Network error fetching {feed_config['url']}: {e}")
        return

    if r.status_code != 200:
        logging.warning(f"Failed to fetch content from {feed_config['url']} - Status: {r.status_code}")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    logging.info(f"HTML parsed, length: {len(str(soup))} characters")

    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []
    dates = soup.select(feed_config["item_date_css"]) if feed_config["item_date_css"] else []
    extras = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []
    stitles = soup.select(feed_config["item_stitle_css"]) if "item_stitle_css" in feed_config else []

    logging.info(f"Found {len(titles)} titles: {[t.text.strip() for t in titles[:3]]}")
    logging.info(f"Found {len(urls)} URLs: {[u.get('href') for u in urls[:3]]}")
    logging.info(f"Found {len(descriptions)} descriptions: {[d.text.strip()[:50] for d in descriptions[:3]]}")
    logging.info(f"Found {len(dates)} dates: {[d.text.strip() for d in dates[:3]]}")

    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    output_data = []

    min_len = min(len(titles), len(urls) or len(titles), len(descriptions) or len(titles), 
                  len(authors) or len(titles), len(dates) or len(titles), len(extras) or len(titles), 
                  len(extras2) or len(titles), len(stitles) or len(titles))
    logging.info(f"Min length for iteration: {min_len}")

    for i in range(min_len):
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]
        entry_id = generate_entry_id(titles[i].text)
        logging.info(f"Processing entry {i+1}: Title='{titles[i].text}', ID={entry_id}")

        fe = fg.add_entry()
        fe.title(f"{titles[i].text} - {stitles[i].text}" if i < len(stitles) else titles[i].text)
        fe.id(entry_id)
        fe.link(href=item_url, rel='alternate')

        description_text = descriptions[i].text if i < len(descriptions) else "No description found"
        description_text = BeautifulSoup(description_text, 'html.parser').text.strip()

        if extras:
            extra_text = extras[i].text if i < len(extras) else "No extra information found"
            description_text += f"\n {extra_text}"
        
        if extras2:
            extra2_text = extras2[i].text if i < len(extras2) else "No second extra information found"
            description_text += f"\n {extra2_text}"

        fe.description(description_text)

        if authors:
            author_text = authors[i].text if i < len(authors) else "No author found"
            fe.author(name=author_text)

        entry_data = {
            "Title": fe.title(),
            "ID": entry_id,
            "Description": description_text
        }
        if authors:
            entry_data["Author"] = author_text
        output_data.append(entry_data)

    logging.info(f"Processed {len(fg.entry())} entries in FeedGenerator, {len(output_data)} entries in output_data")

    os.makedirs(feed_config["output_path"], exist_ok=True)
    fg.atom_file(atom_file_path, overwrite=True)
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)
    logging.info(f"Updated '{atom_file_path}' with {len(fg.entry())} entries.")
    logging.info(f"Updated '{json_file_path}' with {len(output_data)} entries.")

    if should_print_last_entries and len(output_data) > 0:
        logging.info("\n📌 Last 3 entries:")
        for entry in output_data[-3:]:
            logging.info(f"🔹 Title: {entry['Title']}")
            logging.info(f"🔹 URL: {entry['ID']}")
            logging.info(f"🔹 Description: {entry['Description']}")
            logging.info("-" * 50)

def report_git_changes():
    if not GIT_AVAILABLE:
        logging.info("\n⚠️ Git change reporting skipped.")
        return
    try:
        repo = Repo(os.getcwd())
        if repo.is_dirty(untracked_files=True):
            logging.info("\n📝 Git Changes Detected:")
            diff = repo.git.status('--short')
            logging.info(diff)
            logging.info("\n🔍 Summary:")
            logging.info(repo.git.diff('--stat'))
        else:
            logging.info("\n✅ No changes detected in the Git repository.")
    except Exception as e:
        logging.error(f"Error accessing Git repository: {e}")
        sys.exit(1)

try:
    for feed_config in feeds:
        generate_feed(feed_config, should_print_last_entries=should_print_last_entries)
    report_git_changes()
except Exception as e:
    logging.error(f"Main execution failed: {e}")
    sys.exit(1)
