import os
import json
from datetime import datetime
from urllib.parse import urljoin
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import feedparser

from feed import feeds

# Set the flag at the beginning of the script
should_print_last_entries = False  # Change to False/True to skip printing the last entries

# Define the function to generate the feed
def generate_feed(feed_config, should_print_last_entries=False):
    r = requests.get(feed_config["url"])

    # Check if the response status code is 403, 503, or empty
    if r.status_code in [403, 503] or not r.text.strip():
        print(f"Error: Received status code {r.status_code} or empty response for URL: {feed_config['url']}")
        return  # Exit the function if there's an error

    # Parse the response content using BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract relevant data using CSS selectors from the feed configuration
    titles = soup.select(feed_config["item_title_css"])
    urls = soup.select(feed_config["item_url_css"])
    descriptions = soup.select(feed_config["item_description_css"]) if feed_config["item_description_css"] else []
    authors = soup.select(feed_config["item_author_css"]) if feed_config["item_author_css"] else []

    # Initialize the FeedGenerator to generate the RSS feed
    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})

    atom_file_path = os.path.join(feed_config["output_path"], 'atom.xml')
    existing_ids = set()  # Track existing entry IDs to avoid duplicates
    output_data = []  # Store feed entries' data

    # Iterate through the feed entries
    min_len = min(len(titles), len(urls), len(descriptions), len(authors))

    for i in range(min_len):
        item_url = urljoin(feed_config["url"], urls[i].get('href')) if urls else feed_config["url"]

        if item_url in existing_ids:
            continue  # Skip entries that have already been processed

        fe = fg.add_entry()
        fe.title(titles[i].text)
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        description_text = descriptions[i].text if i < len(descriptions) else "No description found"
        fe.description(description_text)

        if authors:
            fe.author(name=authors[i].text if i < len(authors) else "No author found")

        entry_data = {
            "Title": fe.title(),
            "ID": item_url,
            "Description": description_text
        }
        if authors:
            entry_data["Author"] = authors[i].text if i < len(authors) else "No author found"
        output_data.append(entry_data)

        existing_ids.add(item_url)

    # Ensure the output directory exists
    output_path = feed_config["output_path"]
    os.makedirs(output_path, exist_ok=True)
    
    fg.atom_file(atom_file_path)

    json_file_path = os.path.join(output_path, 'feed.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    print(f"XML file '{atom_file_path}' updated successfully.")
    print(f"JSON file '{json_file_path}' created successfully.")

    # Inside the generate_feed function, replace print_last_entries with should_print_last_entries
    if should_print_last_entries and len(output_data) > 0:
        print("\n📌 Last 3 entries:")
        for entry in output_data[-3:]:
            entry_date = datetime.strptime(entry["Date"], '%Y-%m-%d %H:%M:%S') if entry.get("Date") else datetime.now()
            age_days = (datetime.now() - entry_date).days
            is_old = age_days > 30  # Consider "old" if older than 30 days

            print(f"🔹 Title: {entry['Title']}")
            print(f"🔹 URL: {entry['ID']}")
            print(f"🔹 Description: {entry['Description']}")
            
            if 'Date' in entry:
                entry_date = datetime.strptime(entry["Date"], '%Y-%m-%d %H:%M:%S')
                age_days = (datetime.now() - entry_date).days
                
                if age_days > 3:
                    status = "🔴 Old"  # Red for old entries (older than 3 days)
                else:
                    status = "🟢 Recent"  # Green for recent entries (within 3 days)
                
                print(f"🔹 Date: {entry['Date']}")
            else:
                print("🔹 Date: Not available")
                status = "🟡 No Date Available"  # Yellow for missing date

            print(f"🔹 Status: {status}")
            if 'Author' in entry:
                print(f"🔹 Author: {entry['Author']}")
            print(f"🔹 Status: {'🔴 Old' if is_old else '🟢 Recent'} (Age: {age_days} days)")
            print("-" * 50)

for feed_config in feeds:
    generate_feed(feed_config, should_print_last_entries=should_print_last_entries)
