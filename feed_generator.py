import os
from urllib.parse import urljoin
from datetime import datetime
import requests
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from pytz import timezone
import json

def generate_feed(title, subtitle, url, author_name, author_email, language,
                  item_title_selector, item_url_selector, item_author_selector=None,
                  item_description_selector=None, item_date_selector=None,
                  item_date_format=None, item_timezone=None, output_filename='atom.xml'):
    # Make request and parse HTML
    r = requests.get(url)
    r.raise_for_status()  # Raise an exception for non-200 status codes
    soup = BeautifulSoup(r.text, 'html.parser')

    # Select elements based on CSS selectors
    titles = soup.select(item_title_selector)
    urls = soup.select(item_url_selector)
    descriptions = soup.select(item_description_selector or '')
    authors = soup.select(item_author_selector or '')
    dates = soup.select(item_date_selector or '')

    # Initialize FeedGenerator
    fg = FeedGenerator()
    fg.id(url)
    fg.title(title)
    fg.description(subtitle or 'Generated by GitHub Action')
    fg.link(href=url, rel='alternate')
    fg.language(language)
    fg.author({'name': author_name, 'email': author_email})

    # List to hold JSON feed items
    json_items = []

    # Iterate through items and add entries to the feed
    for i, item_title in enumerate(titles):
        if i >= len(urls):  # Check if index is within bounds
            break

        fe = fg.add_entry()
        fe.title(item_title.text.strip())
        item_url = urljoin(url, urls[i].get('href'))
        fe.id(item_url)
        fe.link(href=item_url, rel='alternate')

        description = descriptions[i].text.strip() if descriptions and i < len(descriptions) else ''
        author_name_text = authors[i].text.strip() if authors and i < len(authors) else ''
        date_str = dates[i].text.strip() if dates and i < len(dates) else ''

        if description:
            fe.description(description)

        if author_name_text:
            fe.author(name=author_name_text)

        if date_str and item_date_format:
            date = datetime.strptime(date_str, item_date_format)
        else:
            date = datetime.utcnow()

        localtz = timezone(item_timezone) if item_timezone else timezone('UTC')
        date = localtz.localize(date)
        fe.published(date)
        fe.updated(date)

        # Add to JSON feed items
        json_items.append({
            "title": item_title.text.strip(),
            "url": item_url,
            "description": description,
            "author": {"name": author_name_text},
            "date_published": date.isoformat()
        })

    # Generate Atom feed file with specified output filename structure
    feed_dir = os.path.join('feed', title.lower().replace(' ', '_'))
    os.makedirs(feed_dir, exist_ok=True)
    atom_filepath = os.path.join(feed_dir, 'atom.xml')
    json_filepath = os.path.join(feed_dir, 'feed.json')
    fg.atom_file(atom_filepath)

    # Write JSON feed file
    json_feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": title,
        "home_page_url": url,
        "feed_url": json_filepath,
        "description": subtitle or 'Generated by GitHub Action',
        "items": json_items
    }
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(json_feed, f, ensure_ascii=False, indent=4)

# Example usage
generate_feed(
    title='Sample RSS Feed',
    subtitle='This is a sample RSS feed generated by GitHub Action',
    url='https://www.example.com/',
    author_name='John Doe',
    author_email='john.doe@example.com',
    language='en',
    item_title_selector='.post-title',  # Example CSS selector for item title
    item_url_selector='.post-title a',  # Example CSS selector for item URL
    item_description_selector='.post-content',  # Example CSS selector for item description
    item_author_selector='.post-author',  # Example CSS selector for item author
    item_date_selector='.post-date',  # Example CSS selector for item date
    item_date_format='dd MMM yyyy',  # Date format for items
    item_timezone='UTC',  # Timezone for items
    output_filename='atom.xml'  # Output filename for the RSS feed
)
