import os
import json
import hashlib
import requests
from datetime import datetime
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import feedparser

from feed import feeds

# Set the flag at the beginning of the script
should_print_last_entries = False  # Change to False/True to skip printing the last entries

# Define a function to generate a unique ID for each entry using only the title
def generate_entry_id(title):
    # Create a unique hash based on title only
    unique_string = title.strip()
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

# Define a function to load cache data
def load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as cache_file:
            return json.load(cache_file)
    return {}

# Define a function to save cache data
def save_cache(cache_data, cache_path):
    with open(cache_path, 'w') as cache_file:
        json.dump(cache_data, cache_file, indent=4)

# Define the function to generate the feed
def generate_feed(feed_config, should_print_last_entries=False):
    # Cache file path
    cache_path = os.path.join(feed_config["output_path"], 'feed_cache.json')
    cache_data = load_cache(cache_path)

    # Perform the HTTP request to fetch the feed with ETag caching
    headers = {}
    if 'etag' in cache_data:
        headers['If-None-Match'] = cache_data['etag']

    r = requests.get(feed_config["url"], headers=headers)

    # Print the status code of the request
    print(f"Fetching {feed_config['url']} - Status Code: {r.status_code}")
    
    # If no new content (304 Not Modified), return early
    if r.status_code == 304:
        print("No new content since the last fetch.")
        return

    # Parse the feed content
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract feed item elements based on CSS selectors
    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []
    dates = soup.select(feed_config["item_date_css"]) if feed_config["item_date_css"] else []
    extras = soup.select(feed_config["item_extra_css"]) if "item_extra_css" in feed_config else []
    extras2 = soup.select(feed_config["item_extra_css2"]) if "item_extra_css2" in feed_config else []
    stitles = soup.select(feed_config["item_stitle_css"]) if "item_stitle_css" in feed_config else []

    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    atom_file_path = os.path.join(feed_config["output_path"], 'atom.xml')
    output_data = []

    # Update the cache with the new ETag
    if 'etag' in r.headers:
        cache_data['etag'] = r.headers['etag']
        save_cache(cache_data, cache_path)

    min_len = min(len(titles), len(urls) or len(titles), len(descriptions) or len(titles), len(authors) or len(titles), len(dates) or len(titles), len(extras) or len(titles), len(extras2) or len(titles), len(stitles) or len(titles))

    for i in range(min_len):
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]

        # Generate a unique entry ID using only the title
        entry_id = generate_entry_id(titles[i].text)

        if entry_id not in cache_data:
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
            cache_data[entry_id] = True  # Mark entry as seen

    # Save the updated cache data
    save_cache(cache_data, cache_path)

    # Save the generated feed as an Atom file
    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)
    fg.atom_file(atom_file_path)

    # Save the feed data as JSON
    json_file_path = os.path.join(output_path, 'feed.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    print(f"XML file '{atom_file_path}' updated successfully.")
    print(f"JSON file '{json_file_path}' created successfully.")

    # Inside the generate_feed function, replace print_last_entries with should_print_last_entries
    if should_print_last_entries and len(output_data) > 0:
        print("\n📌 Last 3 entries:")
        for entry in output_data[-3:]:
            print(f"🔹 Title: {entry['Title']}")
            print(f"🔹 URL: {entry['ID']}")
            print(f"🔹 Description: {entry['Description']}")
            print("-" * 50)

for feed_config in feeds:
    generate_feed(feed_config, should_print_last_entries=should_print_last_entries)
