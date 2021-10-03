class BaseConfig(object):
    URL_CACHE_DIRECTORY = None

    # when RANGE_START is None, takes last scrap date from log + 1 dat or today - RESCRAPE_WINDOW days which ever is ealiest
    # keeps scraping until today or RANGE_END whicever is ealiest
    RANGE_START = None
    RANGE_END = None
    RESCRAPE_WINDOW = None 
    MAX_RANGE_LENGTH = None
    BEGINNING_OF_TIME = None
    TELEGRAM_ALLOW = None
    TELEGRAM_TOKEN = None
    TELEGRAM_CHAT_ID = None

