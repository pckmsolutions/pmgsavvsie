from pmgsavvsie.baseconfig import BaseConfig

config = 'config.DevConfig'

class DevConfig(BaseConfig):

    RANGE_START = '2021-09-04'
    RANGE_END = '2021-09-04'
    #RESCRAPE_WINDOW = 5 
    URL_CACHE_DIRECTORY = 'url_cache'
    MAX_RANGE_LENGTH = 1
    BEGINNING_OF_TIME = '2020-01-01'
