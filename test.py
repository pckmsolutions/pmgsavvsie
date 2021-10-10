import logging
import asyncio
import aiohttp
from configparser import ConfigParser
from pmgsavvsie.modules.rb import RbScrape
from pmgsavvsie.scrape import scrape_mod, ScrapeConfig
from pmgsavvsie.test_model import MyDb

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

config = ConfigParser()
config.read('config/testconfig.cfg')

async def main():
    try:
        async with aiohttp.ClientSession() as client_session:
            def_conf = config['default']
            rbscrape = RbScrape(client_session, def_conf['url_cache_directory'])
            module = 'rbscrape'
            scrape_config = ScrapeConfig(
                    def_conf.get('rescrape_window'),
                    def_conf.get('beginning_of_time'),
                    def_conf.get('max_range_length'),
                    def_conf.get('range_start'),
                    def_conf.get('range_end'),
                    )
            ctxs = await scrape_mod(MyDb, module, rbscrape, scrape_config)
    except Exception as e:
        logger.exception(f'Savvsie scrape run failed. {e}')

if __name__ == '__main__':
    asyncio.run(main())

