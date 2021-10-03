from logging import getLogger
from collections import namedtuple

from .model import SavvsieDb

logger = getLogger(__name__)

Event = namedtuple('Event', 'event date_scraped results')

class MyDb(SavvsieDb):
    def __init__(self):
        self.events = []

    def latest_scrape_date(self, mod):
        return None

    def error(self, log_id, event_id, message):
        pass

    def start_mod(self, module, date_scrape):
        return 0

    def fin_mod(self, count, log_id):
        pass

    def start_event(self, event, date_scrape):
        self.events.append(Event(event, date_scrape, []))
        return len(self.events)

    def fin_event(self, event_id):
        event = self.events[event_id - 1]
        results = event.results
        if not results:
            logger.info('Event %s (%s) has no windmilers - disgarding', event.event.name, event.event.date)
            del self.events[event_id - 1]
            return

        logger.info('Event %s (%s) has windmilers', event.event.name, event.event.date)
        for result in event.results:
            logger.info('%s', result)
        

    def result(self, event_id, result_dict):
        if result_dict['club'] == 'Wimbledon Windmilers':
            self.events[event_id - 1].results.append(result_dict)


