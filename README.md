# RSS ONCE A DAY

Inspired by TabHub Rssify (https://tabhub.github.io/)


#edit as you need

feeds = [
    {
        "title": "Palavra do Dia RSS",  # The title of the RSS feed
        "subtitle": "Daily words from Dicio",  # A brief description or subtitle of the feed
        "url": "https://www.dicio.com.br/palavra-do-dia/",  # The URL of the website to scrape for feed data
        "author_name": "Dicio",  # The name of the feed's author
        "author_email": "contact@dicio.com.br",  # The email address of the feed's author
        "copyright": "Dicio",  # The copyright information for the feed
        "language": "pt",  # The language of the feed content, using ISO 639-1 codes
        "item_title_css": ".word-of-day .title",  # CSS selector for the title of each feed item
        "item_url_css": ".word-of-day .title a",  # CSS selector for the URL of each feed item
        "item_author_css": None,  # CSS selector for the author of each feed item (None if not applicable)
        "item_description_css": ".word-of-day--text-wrap .word-of-day--description",  # CSS selector for the description of each feed item
        "item_date_css": ".word-of-day .title",  # CSS selector for the publication date of each feed item
        "item_date_format": "%d/%m/%Y",  # The format of the date string as it appears in the HTML (used with datetime.strptime)
        "item_timezone": "America/Sao_Paulo",  # The timezone of the date information
        "output_path": "feeds/palavra_do_dia",  # The directory path where the generated feed files will be saved
        "formats": ["xml", "json"]  # The formats in which the feed should be generated (e.g., "xml" and/or "json")
    }
]

