import os
import json
import hashlib
import requests
from datetime import datetime
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import feedparser

try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: 'gitpython' module not found. Git change reporting will be skipped.")

from feed import feeds

should_print_last_entries = True  # Set to True to see entries in logs

def generate_entry_id(title):
    unique_string = title.strip()
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as cache_file:
            return json.load(cache_file)
    return {}

def save_cache(cache_data, cache_path):
    with open(cache_path, 'w') as cache_file:
        json.dump(cache_data, cache_file, indent=4)

def generate_feed(feed_config, should_print_last_entries=False):
    cache_path = os.path.join(feed_config["output_path"], 'feed_cache.json')
    cache_data = load_cache(cache_path)
    print(f"Cache loaded: {len(cache_data)} entries in {cache_path}")

    headers = {}
    if 'etag' in cache_data:
        headers['If-None-Match'] = cache_data['etag']

    r = requests.get(feed_config["url"], headers=headers)
    print(f"Fetching {feed_config['url']} - Status Code: {r.status_code}")
    print(f"Response length: {len(r.text)} characters")

    if r.status_code == 304:
        print("No new content since the last fetch.")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"HTML parsed, length: {len(str(soup))} characters")

    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []
    dates = soup.select(feed_config["item_date_css"]) if feed_config["item_date_css"] else []
    extras = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []
    stitles = soup.select(feed_config["item_stitle_css"]) if "item_stitle_css" in feed_config else []

    print(f"Found {len(titles)} titles: {[t.text.strip() for t in titles[:3]]}")
    print(f"Found {len(urls)} URLs: {[u.get('href') for u in urls[:3]]}")
    print(f"Found {len(descriptions)} descriptions: {[d.text.strip()[:50] for d in descriptions[:3]]}")
    print(f"Found {len(dates)} dates: {[d.text.strip() for d in dates[:3]]}")

    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    output_data = []

    if 'etag' in r.headers:
        cache_data['etag'] = r.headers['etag']
        save_cache(cache_data, cache_path)

    min_len = min(len(titles), len(urls) or len(titles), len(descriptions) or len(titles), 
                  len(authors) or len(titles), len(dates) or len(titles), len(extras) or len(titles), 
                  len(extras2) or len(titles), len(stitles) or len(titles))
    print(f"Min length for iteration: {min_len}")

    for i in range(min_len):
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]
        entry_id = generate_entry_id(titles[i].text)
        print(f"Processing entry {i+1}: Title='{titles[i].text}', ID={entry_id}")

        if entry_id not in cache_data:
            print(f"New entry detected: {entry_id}")
            fe = fg.add_entry()
            fe.title(f"{titles[i].text} - {stitles[i].text}" if i < len(stitles) else titles[i].text)
            fe.id(entry_id)
            fe.link(href=item_url, rel='alternate')

            description_text = descriptions[i].text if i < len(descriptions) else "No description found"
            description_text = BeautifulSoup(description_text, 'html.parser').text.strip()
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
            cache_data[entry_id] = True
        else:
            print(f"Entry {entry_id} already in cache, skipping.")

    save_cache(cache_data, cache_path)

    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)
    atom_file_path = os.path.join(output_path, 'atom.xml')
    fg.atom_file(atom_file_path)

    if os.path.exists(atom_file_path) and os.path.getsize(atom_file_path) > 0:
        print(f"XML file '{atom_file_path}' updated successfully with {len(fg.entry())} entries.")
    else:
        print(f"Error: XML file '{atom_file_path}' was not created or is empty.")

    json_file_path = os.path.join(output_path, 'feed.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
        print(f"JSON file '{json_file_path}' created successfully with {len(output_data)} entries.")
    else:
        print(f"Error: JSON file '{json_file_path}' was not created or is empty.")

    if should_print_last_entries and len(output_data) > 0:
        print("\n📌 Last 3 entries:")
        for entry in output_data[-3:]:
            print(f"🔹 Title: {entry['Title']}")
            print(f"🔹 URL: {entry['ID']}")
            print(f"🔹 Description: {entry['Description']}")
            print("-" * 50)

def report_git_changes():
    if not GIT_AVAILABLE:
        print("\n⚠️ Git change reporting skipped due to missing 'gitpython' module.")
        return
    try:
        repo = Repo(os.getcwd())
        if repo.is_dirty(untracked_files=True):
            print("\n📝 Git Changes Detected:")
            diff = repo.git.status('--short')
            print(diff)
            print("\n🔍 Summary:")
            print(repo.git.diff('--stat'))
        else:
            print("\n✅ No changes detected in the Git repository.")
    except Exception as e:
        print(f"Error accessing Git repository: {e}")

for feed_config in feeds:
    generate_feed(feed_config, should_print_last_entries=should_print_last_entries)

report_git_changes()
