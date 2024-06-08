feeds = [
    {
        "title": "Palavra do Dia RSS",
        "subtitle": "Palavra do Dia por Dicio",
        "url": "https://www.dicio.com.br/palavra-do-dia/",
        "author_name": "Lau",
        "author_email": "None",
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
    },
    {
    "title": "Versículo do Dia",
    "subtitle": "Versículo do Dia por biblia on",
    "url": "https://www.bibliaon.com/versiculo_do_dia/",
    "author_name": "Lau",
    "author_email": "author@example.com",
    "copyright": "Biblia",
    "language": "pt",
    "item_title_css": ".v_dia .destaque a",
    "item_url_css": ".v_dia .destaque a",
    "item_author_css": "",
    "item_description_css": ".v_dia .destaque",
    "item_date_css": ".v_dia .v_date",
    "item_date_format": "%A, %d de %B de %Y",
    "item_timezone": "GMT-3",
    "output_path": "feeds/versículo_do_dia",
    "formats": ["xml", "json"]
}

]
