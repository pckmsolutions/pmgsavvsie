from itertools import count
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import unicodedata
import os
from logging import getLogger

from ..core import KnownColumns, ResultRow

logger = getLogger(__name__)

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def parse_date(strng):
    try:
        return parse(strng).date()
    except:
        pass
    return ''

def cvt_to_result_row(columns):
    mapper = {next((kcol.name for kcol in KnownColumns if col in kcol.value), ''): ind for col, ind in zip(columns, count())}

    def cvt(row):
        def mapval(kcol):
            ind = mapper.get(kcol.name)
            return kcol.name, row[ind] if ind != None else None

        return ResultRow(dict([mapval(kcol) for kcol in KnownColumns]))

    return cvt

class BsForUrlFunc(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, url):
        try:
            return BeautifulSoup(self.requests_get_text(url), features='html.parser')
        except RequestException as err:
            logger.error(f'Bad url {url}')
            raise err

    def clean_filename(self, filename, whitelist=valid_filename_chars, replace=' '):
        # replace spaces
        for r in replace:
            filename = filename.replace(r,'_')
        
        # keep only valid ascii chars
        cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
        
        # keep only whitelisted chars
        cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
        if len(cleaned_filename)>char_limit:
            print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
        return cleaned_filename[:char_limit]    
    
    def requests_get_text(self, url):
        if self.config.URL_CACHE_DIRECTORY:
            cache_filename = os.path.join(self.config.URL_CACHE_DIRECTORY, self.clean_filename(url))
            try:
                with open(cache_filename, 'r') as f:
                    logger.info(f'Using cached data for {url} from {cache_filename}')
                    return f.read()
            except IOError:
                pass
    
        text = requests.get(url).text

        if self.config.URL_CACHE_DIRECTORY:
            with open(cache_filename, 'w+') as f:
                logger.info(f'Caching data for {url} to {cache_filename}')
                f.write(text)
    
        return text


def get_range(config, last_scrape):
    if config.RESCRAPE_WINDOW != None:
        today = datetime.utcnow().date()
        if not last_scrape:
            assert config.BEGINNING_OF_TIME != None, 'No scrape yet - must have beginning of time'
            logger.info(f'First scrape - starting from {config.BEGINNING_OF_TIME}')
            date_from = datetime.strptime(config.BEGINNING_OF_TIME, '%Y-%m-%d').date()
        else:
            date_from = min(last_scrape + timedelta(days=1), today - timedelta(days=config.RESCRAPE_WINDOW))
            logger.info(f'Last scrape  {last_scrape} - starting from {date_from}')
    
        if config.MAX_RANGE_LENGTH != None:
            assert config.MAX_RANGE_LENGTH > 0, 'range length must be at least 1'
            date_to = min(date_from + timedelta(days=config.MAX_RANGE_LENGTH - 1 ), today)
        else:
            date_to = today
    
    elif config.RANGE_START and config.RANGE_END:
        date_from = datetime.strptime(config.RANGE_START, '%Y-%m-%d').date()
        date_to = datetime.strptime(config.RANGE_END, '%Y-%m-%d').date()
    else:
        logger.error('Can''t scrape. need either re-scrape window or range')
        return

    logger.info(f'Date range from {date_from} to {date_to} (in reverse order)')
    return date_from, date_to

def get_dates(config, last_scrape):
    date_from, date_scrape = get_range(config, last_scrape)

    while date_scrape >= date_from:
        yield date_scrape
        date_scrape -= timedelta(days=1)


