feeds = [
    {
        "title": "Palavra do Dia RSS",
        "subtitle": "Palavra do Dia por Dicio",
        "url": "https://www.dicio.com.br/palavra-do-dia/",
        "author_name": "Lau",
        "author_email": " ",
        "copyright": "Dicio",
        "language": "pt-BR",  # Changed from "pt"
        "item_title_css": ".word-of-day .title",
        "item_stitle_css": ".word-of-day--subtitle",
        "item_url_css": ".word-of-day--subtitle a",
        "item_author_css": "",  # Changed from None
        "item_description_css": ".word-of-day--text-wrap .word-of-day--description, .word-of-day--extra",
        "item_extra_css": ".word-of-day--extra",
        "item_extra_css2": "",  # Changed from None
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
        "language": "en",  # Kept as "en" since it’s not Portuguese
        "item_title_css": ".feed-item .title",
        "item_stitle_css": "",  # Changed from None
        "item_url_css": ".feed-item .link",
        "item_author_css": ".feed-item .author",
        "item_description_css": ".feed-item .description",
        "item_extra_css": "",  # Changed from None
        "item_extra_css2": "",  # Changed from None
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
        "language": "pt-BR",  # Changed from "pt"
        "item_title_css": ".v_dia .destaque a",
        "item_stitle_css": "",  # Changed from None
        "item_url_css": ".v_dia .destaque a",
        "item_author_css": "",
        "item_description_css": ".v_dia .destaque",
        "item_extra_css": "",  # Changed from None
        "item_extra_css2": "",  # Changed from None
        "item_date_css": ".v_dia .v_date:nth-child(2)",
        "item_date_format": "%d de %B de %Y",
        "item_timezone": "GMT-3",
        "output_path": "feeds/versículo_do_dia",
        "formats": ["xml", "json"]
    },
    {
        "title": "Salmo do Dia",
        "subtitle": "Salmo do Dia por biblia on",
        "url": "https://www.bibliaon.com/salmo_do_dia/",
        "author_name": "Lau",
        "author_email": "author@example.com",
        "copyright": "Biblia",
        "language": "pt-BR",  # Changed from "pt"
        "item_title_css": ".salmo_dia_card_content_link",
        "item_stitle_css": "",  # Changed from None
        "item_url_css": ".salmo_dia_card_content_link",
        "item_author_css": "",
        "item_description_css": ".salmo_dia_card_content",
        "item_extra_css": "",  # Changed from None
        "item_extra_css2": "",  # Changed from None
        "item_date_css": ".salmo_dia_card_date",
        "item_date_format": "%A, %d de %B de %Y",
        "item_timezone": "GMT-3",
        "output_path": "feeds/salmo_do_dia",
        "formats": ["xml", "json"]
    },
    {
        "title": "Palavra Biblica do Dia",
        "url": "https://www.bibliaon.com/palavra_do_dia/",
        "output_path": "feeds/palavra_biblica_do_dia",
        "subtitle": "Inspiração diária da Palavra de Deus",
        "language": "pt-BR",  # Already "pt-BR", kept as is
        "author_name": "BíbliaOn",
        "author_email": "contato@bibliaon.com",
        "item_title_css": ".word-day .v_title.v_title_word",
        "item_stitle_css": ".word-day .v_title:not(.v_title_word)",
        "item_url_css": ".word-day .sg-social[data-url]",
        "item_description_css": ".word-day .destaque.articlebody",
        "item_extra_css": ".word-day .destaque.articlebody ul",
        "item_extra_css2": ".word-day .destaque.articlebody blockquote",
        "item_author_css": "",  # Changed from None
        "item_date_css": ".word-day .v_date",
        "item_date_format": "%d de %B de %Y",
        "item_timezone": "GMT-3",
        "formats": ["xml", "json"]
    },
    {
        "title": "Devocional de Hoje",
        "subtitle": "Devocional de Hoje por biblia on",
        "url": "https://www.bibliaon.com/devocional_diario/",
        "author_name": "Lau",
        "author_email": "author@example.com",
        "copyright": "Biblia",
        "language": "pt-BR",  # Changed from "pt"
        "item_title_css": "div.dev-day .dev-title",
        "item_stitle_css": "",  # Changed from None
        "item_url_css": "div.dev-day .articlebody a",
        "item_author_css": "",
        "item_description_css": "div.dev-day .articlebody",
        "item_extra_css": "",  # Changed from None
        "item_extra_css2": "",  # Changed from None
        "item_date_css": "div.dev-day .devcal-wrap",
        "item_date_format": "%A, %d de %B de %Y",
        "item_timezone": "GMT-3",
        "output_path": "feeds/devocional_de_hoje",
        "formats": ["xml", "json"]
    },
# Wikipedia Feeds with corrected selectors
    {
        "url": "https://pt.wikipedia.org/wiki/Wikipédia:Página_principal",
        "output_path": "feeds/wikidestaque",
        "title": "Wikipédia em Português - Artigo em Destaque",
        "subtitle": "Artigo em destaque da Wikipédia em português",
        "language": "pt-BR",
        "author_name": "Comunidade Wikipédia",
        "author_email": "contato@wikipedia.org",
        "item_title_css": "div.main-page-first-row div:first-child .main-page-block-heading",  # Only first column of first row
        "item_stitle_css": "",
        "item_url_css": "div.main-page-first-row div:first-child .main-page-block-contents a[href*='/wiki/']",  # First column links
        "item_author_css": "",
        "item_description_css": "div.main-page-first-row div:first-child .main-page-block-contents",  # First column content
        "item_extra_css": "",
        "item_extra_css2": "",
        "item_date_css": "",
        "item_date_format": "",
        "item_timezone": "",
        "formats": ["xml", "json"]
    },
    {
        "url": "https://pt.wikipedia.org/wiki/Wikipédia:Página_principal",
        "output_path": "feeds/wikidia",
        "title": "Wikipédia em Português - Efemérides",
        "subtitle": "Efemérides diárias da Wikipédia em português",
        "language": "pt-BR",
        "author_name": "Comunidade Wikipédia",
        "author_email": "contato@wikipedia.org",
        "item_title_css": "div.main-page-second-row div:first-child .main-page-block-heading",  # Only first column of second row
        "item_stitle_css": "",
        "item_url_css": "div.main-page-second-row div:first-child .main-page-block-contents a[href*='/wiki/']",  # First column links
        "item_author_css": "",
        "item_description_css": "div.main-page-second-row div:first-child .main-page-block-contents",  # First column content
        "item_extra_css": "",
        "item_extra_css2": "",
        "item_date_css": "",
        "item_date_format": "",
        "item_timezone": "",
        "formats": ["xml", "json"]
    },
    {
        "url": "https://pt.wikipedia.org/wiki/Wikipédia:Página_principal",
        "output_path": "feeds/wikiimagem",
        "title": "Wikipédia em Português - Imagem do Dia",
        "subtitle": "Imagem do dia da Wikipédia em português",
        "language": "pt-BR",
        "author_name": "Comunidade Wikipédia",
        "author_email": "contato@wikipedia.org",
        "item_title_css": "div.main-page-third-row div .main-page-block-heading",  # Third row heading (unchanged, works fine)
        "item_stitle_css": "",
        "item_url_css": "div.main-page-third-row div .main-page-block-contents a[href*='/wiki/Ficheiro:']",  # Third row file link (unchanged)
        "item_author_css": "",
        "item_description_css": "div.main-page-third-row div .main-page-block-contents",  # Third row content (unchanged)
        "item_extra_css": "",
        "item_extra_css2": "",
        "item_date_css": "",
        "item_date_format": "",
        "item_timezone": "",
        "formats": ["xml", "json"]
    }
]
