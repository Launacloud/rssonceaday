import os
import json
import logging
from datetime import datetime
from urllib.parse import urljoin
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import feedparser
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
from dataclasses import dataclass

# Assuming feeds is imported from feed.py
from feed import feeds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('feed_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FeedConfigError(Exception):
    """Custom exception for feed configuration errors"""
    message: str

class FeedGenerationError(Exception):
    """Custom exception for feed generation errors"""
    pass

def validate_config(feed_config: Dict) -> None:
    """Validate feed configuration"""
    required_fields = ["url", "title", "subtitle", "language", "author_name", 
                      "author_email", "output_path", "item_title_css"]
    missing = [field for field in required_fields if field not in feed_config]
    if missing:
        raise FeedConfigError(f"Missing required fields: {', '.join(missing)}")

@lru_cache(maxsize=32)
def fetch_webpage(url: str, retries: int = 3) -> BeautifulSoup:
    """Fetch webpage content with retries and caching"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise FeedGenerationError(f"Failed to fetch {url} after {retries} attempts: {str(e)}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def extract_elements(soup: BeautifulSoup, css_selector: str) -> List:
    """Extract elements from soup using CSS selector"""
    try:
        return soup.select(css_selector) if css_selector else []
    except Exception as e:
        logger.warning(f"Failed to extract elements with selector {css_selector}: {str(e)}")
        return []

def setup_feed_generator(feed_config: Dict) -> FeedGenerator:
    """Initialize and configure FeedGenerator"""
    fg = FeedGenerator()
    fg.id(feed_config["url"])
    fg.title(feed_config["title"])
    fg.subtitle(feed_config["subtitle"])
    fg.link(href=feed_config["url"], rel='alternate')
    fg.language(feed_config["language"])
    fg.author({'name': feed_config["author_name"], 'email': feed_config["author_email"]})
    return fg

def load_existing_entries(fg: FeedGenerator, atom_file_path: str) -> tuple[set, List]:
    """Load existing feed entries if file exists"""
    existing_ids = set()
    output_data = []
    
    if os.path.exists(atom_file_path):
        try:
            existing_feed = feedparser.parse(atom_file_path)
            for entry in existing_feed.entries:
                fe = fg.add_entry()
                fe.id(entry.id)
                fe.title(entry.title)
                fe.link(href=entry.link)
                fe.description(entry.description)
                
                if hasattr(entry, 'author'):
                    fe.author(name=entry.author)
                if hasattr(entry, 'published'):
                    fe.published(entry.published)
                
                entry_data = {
                    "Title": entry.title,
                    "ID": entry.id,
                    "Description": entry.description,
                    **({"Author": entry.author} if hasattr(entry, 'author') else {})
                }
                output_data.append(entry_data)
                existing_ids.add(entry.id)
        except Exception as e:
            logger.warning(f"Failed to load existing entries from {atom_file_path}: {str(e)}")
    
    return existing_ids, output_data

def generate_feed(feed_config: Dict) -> None:
    """Generate RSS feed from website content and print last 3 entries"""
    try:
        validate_config(feed_config)
        
        # Fetch and parse webpage
        soup = fetch_webpage(feed_config["url"])
        
        # Extract elements
        elements = {
            "titles": extract_elements(soup, feed_config["item_title_css"]),
            "urls": extract_elements(soup, feed_config["item_url_css"]),
            "descriptions": extract_elements(soup, feed_config["item_description_css"]),
            "authors": extract_elements(soup, feed_config["item_author_css"]),
            "dates": extract_elements(soup, feed_config["item_date_css"]),
            "extras": extract_elements(soup, feed_config.get("item_extra_css", "")),
            "extras2": extract_elements(soup, feed_config.get("item_extra_css2", "")),
            "stitles": extract_elements(soup, feed_config.get("item_stitle_css", ""))
        }
        
        if not elements["titles"]:
            raise FeedGenerationError("No titles found - check CSS selectors")
        
        # Initialize feed generator
        fg = setup_feed_generator(feed_config)
        
        # Setup output paths
        output_path = feed_config["output_path"]
        os.makedirs(output_path, exist_ok=True)
        atom_file_path = os.path.join(output_path, 'atom.xml')
        
        # Load existing entries
        existing_ids, output_data = load_existing_entries(fg, atom_file_path)
        
        # Calculate minimum length of all element lists
        min_len = min(len(lst) or float('inf') for lst in elements.values())
        
        # Store new entries for printing
        new_entries = []
        
        # Add new entries
        for i in range(min(min_len, len(elements["titles"]))):
            item_url = urljoin(feed_config["url"], 
                             elements["urls"][i].get('href')) if elements["urls"] else feed_config["url"]
            
            if item_url in existing_ids:
                continue
            
            fe = fg.add_entry()
            title = (f"{elements['titles'][i].text} - {elements['stitles'][i].text}"
                    if i < len(elements["stitles"]) and elements["stitles"]
                    else elements["titles"][i].text)
            fe.title(title)
            fe.id(item_url)
            fe.link(href=item_url, rel='alternate')
            
            # Build description
            description = (BeautifulSoup(elements["descriptions"][i].text, 'html.parser').text.strip()
                         if i < len(elements["descriptions"]) and elements["descriptions"]
                         else "No description found")
            for extra_key, default in [("extras", "No extra information found"),
                                     ("extras2", "No second extra information found")]:
                if elements[extra_key] and i < len(elements[extra_key]):
                    description += f"\n{elements[extra_key][i].text}"
                elif elements[extra_key]:
                    description += f"\n{default}"
            
            fe.description(description)
            author = elements["authors"][i].text if elements["authors"] and i < len(elements["authors"]) else None
            if author:
                fe.author(name=author)
            
            entry_data = {
                "Title": title,
                "ID": item_url,
                "Description": description,
                **({"Author": author} if author else {})
            }
            output_data.append(entry_data)
            new_entries.append(entry_data)
        
        # Print last 3 new entries
        if new_entries:
            logger.info(f"Last 3 new entries from {feed_config['url']}:")
            for entry in new_entries[-3:]:
                logger.info(f"Title: {entry['Title']}")
                logger.info(f"URL: {entry['ID']}")
                logger.info(f"Description: {entry['Description']}")
                if 'Author' in entry:
                    logger.info(f"Author: {entry['Author']}")
                logger.info("-" * 50)
        else:
            logger.info(f"No new entries found for {feed_config['url']}")
        
        # Save outputs
        fg.atom_file(atom_file_path)
        with open(os.path.join(output_path, 'feed.json'), 'w') as json_file:
            json.dump(output_data, json_file, indent=4)
        
        logger.info(f"Successfully updated XML file: {atom_file_path}")
        logger.info(f"Successfully created JSON file: {os.path.join(output_path, 'feed.json')}")
        
    except (FeedConfigError, FeedGenerationError) as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating feed for {feed_config.get('url', 'unknown')}: {str(e)}", 
                    exc_info=True)

def main():
    """Main function to process all feeds in parallel"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(generate_feed, feeds)

# Unit Tests
def test_validate_config():
    invalid_config = {"url": "test.com"}
    try:
        validate_config(invalid_config)
        assert False, "Should raise FeedConfigError"
    except FeedConfigError:
        assert True

def test_fetch_webpage():
    try:
        fetch_webpage("http://example.com")
        assert True
    except FeedGenerationError:
        assert False, "Valid URL should not raise exception"

if __name__ == "__main__":
    # Run tests
    test_validate_config()
    test_fetch_webpage()
    
    # Process feeds
    main()
