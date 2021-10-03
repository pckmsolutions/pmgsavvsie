from pmgsiteinfra import configure_logging
from os import path
configure_logging(path.join(path.dirname(__file__), '../config/logconf.yaml'))
from logging import getLogger

from .scrape import scrape_mod
from .modules.rb import RbScrape
from .test_model import MyDb

logger = getLogger(__name__)


def cronrun(config):
    try:
        rbscrape = RbScrape(config)
        module = 'rbscrape'
        ctxs = scrape_mod(MyDb, module, rbscrape, config)
        #for ctx in ctxs:
        #    if ctx.has_message:
        #        send_message(ctx.message)
    except Exception as e:
        logger.exception(f'Savvsie scrape run failed. {e}')
