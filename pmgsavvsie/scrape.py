from datetime import datetime
import sys
from contextlib import contextmanager
from collections import namedtuple

from .core import KnownColumns
from .util import cvt_to_result_row, parse_date
import logging
from .util import get_dates

logger = logging.getLogger(__name__)

ScrapeConfig = namedtuple('ScrapeConfig',
        'rescrape_window beginning_of_time max_range_length range_start range_end')

def scrape_mod(db_model, module, scraper, scrape_config):
    savvsie_db = db_model()
    dates = get_dates(scrape_config, savvsie_db.latest_scrape_date(module))

    rets = []
    for date_scrape in dates:
        rets.append(scrape_for_date(savvsie_db, module, scraper, date_scrape))

    return rets

def scrape_for_date(savvsie_db, module, scraper, date_scrape):
    class DbLogHandler(logging.StreamHandler):
        def __init__(self, log_id, event_id, savvsie_db):
            super(DbLogHandler, self).__init__()
            self.log_id = log_id
            self.event_id = event_id
            self.savvsie_db = savvsie_db
    
        def emit(self, record):
            self.savvsie_db.error(self.log_id, self.event_id, self.format(record), )

    @contextmanager
    def log_scope(log_id, event_id, savvsie_db):
        dbloghandler = DbLogHandler(log_id, event_id, savvsie_db)
        dbloghandler.setLevel(logging.ERROR)
        logger.addHandler(dbloghandler)
        try:
            yield
        except:
            logger.removeHandler(dbloghandler)
            raise

    logger.info(f'Scraping with module {module} for {date_scrape}')

    class Ctx(object):
        def __init__(self):
            self.module = module
            self.date_scrape = date_scrape
            self.count = 0
            self.inserted_count = 0
            self.started = datetime.utcnow()
            self.finished = None

        @property
        def has_message(self):
            return self.inserted_count > 0

        @property
        def message(self):
            return f'''Savvsie scraped results
Scraped date: {self.date_scrape}
Module: {self.module}
Results: {self.inserted_count}
Started: {self.started}
Finished: {self.finished}
'''

    ctx = Ctx()
    
    ctx.log_id = savvsie_db.start_mod(module, date_scrape)
    
    rbevents = scraper.scrape(date_from=date_scrape, date_to=date_scrape)
    logger.info(f'Module {module} finding events on {date_scrape}')
    
    for event in rbevents:
        ctx.count += 1
        logger.info(f'Processing event: {event.name}')

        event_id = savvsie_db.start_event(event, date_scrape)
        if not event_id:
            continue

        ctx.inserted_count += 1
    
        with log_scope(ctx.log_id, event_id, savvsie_db):
            parsed_event_date = parse_date(event.date)
            if parsed_event_date != date_scrape:
                logger.warning(f'Scrape date ({date_scrape}) and event date ({event.date}/{parsed_event_date}) differ.')
    
            converter = cvt_to_result_row(event.results_columns)
    
            for result_row in event.results:
                result = converter(result_row)
                try:
                    result_dict = result.as_dict(
                            (KnownColumns.POS, KnownColumns.TIME, KnownColumns.NAME, KnownColumns.CLUB),
                            (KnownColumns.AGE_GROUP, KnownColumns.GENDER))
                except ValueError as va:
                    logger.error(f'Value Error with row:{res}. skipping.')
                    continue
    
                result_dict['event_id'] = event_id
                result_dict.setdefault(KnownColumns.AGE_GROUP.name, None)
                result_dict.setdefault(KnownColumns.GENDER.name, None)

                savvsie_db.result(event_id, result_dict)

        savvsie_db.fin_event(event_id)
    
    savvsie_db.fin_mod(ctx.count, ctx.log_id)

    ctx.finished = datetime.utcnow()
    return ctx



