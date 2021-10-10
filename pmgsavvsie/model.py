from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger(__name__)

class SavvsieDb(ABC):
    def __init__(self, **kwargs):
        super(SavvsieDb, self).__init__(**kwargs)

    @abstractmethod
    async def latest_scrape_date(self, mod):
        return None

    @abstractmethod
    def error(self, log_id, event_id, message):
        logger.info('error %s, %s, %s', log_id, event_id, message)
        pass

    @abstractmethod
    async def start_mod(self, module, date_scrape):
        logger.info('start_mod %s, %s', module, date_scrape)
        return 0

    @abstractmethod
    async def fin_mod(self, count, log_id):
        logger.info('fin_mod %s, %s', count, log_id)
        pass

    @abstractmethod
    async def start_event(self, event, date_scrape):
        logger.info('insert_event %s, %s', event, date_scrape)
        return 1

    @abstractmethod
    async def fin_event(self, event_id):
        pass

    @abstractmethod
    async def result(self, result_dict):
        logger.info('insert_result %s', result_dict)
        pass

