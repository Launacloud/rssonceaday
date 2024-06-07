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
        "item_url_css": ".word-of-day--subtitle a",
        "item_author_css": None,
        "item_description_css": ".word-of-day--text-wrap .word-of-day--description, .word-of-day--extra",
        "item_extra_css": ".word-of-day--extra",  # Added item_extra_css for the extra field
        "item_extra_css2": "p.adicional",  # Added item_extra_css2 for the second extra field
        "item_date_css": ".word-of-day .title",
        "item_date_format": "%d/%m/%Y",
        "item_timezone": "America/Sao_Paulo",
        "output_path": "feeds/palavra_do_dia",
        "formats": ["xml", "json"]
    },
    {
        "title": "Example Feed RSS",
        "subtitle": "Example subtitle",
        "url": "https://www.example.com/feed/",
        "author_name": "Example Author",
        "author_email": "author@example.com",
        "copyright": "Example Company",
        "language": "en",
        "item_title_css": ".feed-item .title",
        "item_url_css": ".feed-item .link",
        "item_author_css": ".feed-item .author",
        "item_description_css": ".feed-item .description",
        "item_date_css": ".feed-item .date",
        "item_date_format": "%Y-%m-%d",
        "item_timezone": "UTC",
        "output_path": "feeds/example_feed",
        "formats": ["xml", "json"]
    }
]
