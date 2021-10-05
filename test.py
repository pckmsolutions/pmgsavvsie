from configparser import ConfigParser
from pmgsavvsie.modules.rb import RbScrape
from pmgsavvsie.scrape import scrape_mod, ScrapeConfig
from pmgsavvsie.test_model import MyDb

from logging import getLogger
logger = getLogger(__name__)

config = ConfigParser()
config.read('config/testconfig.cfg')

if __name__ == '__main__':
    try:
        def_conf = config['default']
        rbscrape = RbScrape(def_conf['url_cache_directory'])
        module = 'rbscrape'
        scrape_config = ScrapeConfig(
                def_conf.get('rescrape_window'),
                def_conf.get('beginning_of_time'),
                def_conf.get('max_range_length'),
                def_conf.get('range_start'),
                def_conf.get('range_end'),
                )
        ctxs = scrape_mod(MyDb, module, rbscrape, scrape_config)
    except Exception as e:
        logger.exception(f'Savvsie scrape run failed. {e}')

