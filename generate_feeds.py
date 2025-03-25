def generate_feed(feed_config: Dict) -> None:
    """Generate RSS feed from website content and print last 3 entries with dates"""
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
        
        # Store new entries
        new_entries = []
        current_date = datetime.now()  # Today’s date: March 24, 2025
        
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
            
            # Set publication date if available
            pub_date = (elements["dates"][i].text if elements["dates"] and i < len(elements["dates"])
                       else current_date.strftime('%Y-%m-%d %H:%M:%S'))
            fe.published(pub_date)
            
            entry_data = {
                "Title": title,
                "ID": item_url,
                "Description": description,
                "Date": pub_date,
                **({"Author": author} if author else {})
            }
            output_data.append(entry_data)
            new_entries.append(entry_data)
        
        # Print last 3 entries (new or old) with age check
        if output_data:
            logger.info(f"Last 3 entries from {feed_config['url']} (new or old):")
            for entry in output_data[-3:]:
                entry_date = datetime.strptime(entry["Date"], '%Y-%m-%d %H:%M:%S') if entry["Date"] else current_date
                age_days = (current_date - entry_date).days
                is_old = age_days > 30  # Consider "old" if older than 30 days
                
                logger.info(f"Title: {entry['Title']}")
                logger.info(f"URL: {entry['ID']}")
                logger.info(f"Description: {entry['Description']}")
                logger.info(f"Date: {entry['Date']}")
                if 'Author' in entry:
                    logger.info(f"Author: {entry['Author']}")
                logger.info(f"Status: {'Old' if is_old else 'Recent'} (Age: {age_days} days)")
                logger.info("-" * 50)
        else:
            logger.info(f"No entries found for {feed_config['url']}")
        
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
