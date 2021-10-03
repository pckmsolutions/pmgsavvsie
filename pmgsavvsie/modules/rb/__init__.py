from bs4 import BeautifulSoup
import datetime
import requests
import urllib.parse as urlp
import itertools
import re
from requests.exceptions import RequestException
from ...core import AbstractScraper, AbstractEvent
from ...util import BsForUrlFunc


import logging
logger = logging.getLogger(__name__)

def _tag_with_id(root, tag, tag_id):
    return root.find(lambda t: t.name == tag and \
            tag_id in t.get_attribute_list('id'), \
            recursive=True)

def _table_with_id(root, tab_id):
    return _tag_with_id(root, 'table', tab_id)

class RbEvent(AbstractEvent):
    pass

def flatten_sets(event_sets):
    for event_set in event_sets:
        for event in event_set.get_result_set():
            yield RbEvent(
                    date=event_set.date,
                    name=f'{event_set.name} - {"/".join(event.tags)}',
                    label = event_set.type,
                    distance = dist_from_tag(event.tags[0]),
                    category = 'run',
                    event_url = event_set.event_url,
                    result_url = event_set.result_url,
                    results_columns = event.result_columns,
                    results = event.result_rows)

def dist_from_tag(tag):
    return tag.split(' ', 1)[0] if tag else None

class RbScrape(AbstractScraper):
    BASE_URL = 'https://www.runbritainrankings.com'

    def __init__(self, config):
        self.config = config
        self.bs_for_url = BsForUrlFunc(config)

    def scrape(self, date_from, date_to):
        return flatten_sets(self.get_event_sets(date_from, date_to))

    def get_event_sets(self, date_from, date_to):
        df = lambda d: d.strftime('%-d-%b-%Y')
        url = urlp.urljoin(RbScrape.BASE_URL,
                ('/results/resultslookup.aspx'
                    f'?datefrom={df(date_from)}'
                    f'&dateto={df(date_to)}'
                    '&terraintypecodes=RMPTIX'))
        try:
            bs = self.bs_for_url(url)
        except RequestException:
            return []

        table = _table_with_id(bs, 'cphBody_dgMeetings')

        if not table:
            return []

        for t in table.find_all('tr')[1:]:
            yield RbScrapeEvent(t, self.bs_for_url)
        #return list(map(lambda t : RbScrapeEvent(t), table.find_all('tr')[1:]))

    def get_event_sets_as_list(self, date_from, date_to):
        return list(self.get_event_sets(date_from, date_to))

class RbScrapeEvent(object):
    COL_PAT = re.compile('[A-Za-z0-9]+')
    COL_PAGE_HREF_PAT = re.compile('^.*pagenum=([0-9]+)')
    #CLEAN_NAME_PAT = re.compile(r'(  )+')

    def __init__(self, tr_tag, bs_for_url):
        self.bs_for_url = bs_for_url
        cells = tr_tag.find_all('td')

        def getlink():
            a = cells[1].find('a')
            if not a:
                return None
            links = a.get_attribute_list('href')
            return links[0] if links else None

        def getresulturl():
            a = cells[4].find('a')
            if not a:
                return None
            links = a.get_attribute_list('href')
            if not links:
                return None

            url = urlp.urljoin(RbScrape.BASE_URL, links[0])
            return url

        self.date = cells[0].get_text().strip()
        self.event_url = getlink()
        self.name = ' '.join(cells[1].stripped_strings)
        self.type = ' '.join(cells[3].stripped_strings)
        self.result_url = getresulturl()
        self.cached_result_set = None


    def get_result_set(self):
        if self.cached_result_set:
            return self.cached_result_set

        if not self.result_url:
            logger.info(f'No results URL for event {self.name} on {self.date}')
            return []

        try:
            bs = self.bs_for_url(self.result_url)
        except RequestException:
            logger.info(f'Crap URL {self.result_url} - Returning empty list')
            return []
        
        def get_page_links():
            def link_to_page_tup(a):
                hr = a.get_attribute_list('href')
                if not hr:
                    return None
                m = RbScrapeEvent.COL_PAGE_HREF_PAT.match(hr[0])
                if not m:
                    return None
                return hr[0]

            page_links = _tag_with_id(bs, 'span', 'cphBody_lblBottomPageLinks')
            return [b for b in map(link_to_page_tup, [a for a in page_links.find_all('a')])] if page_links else None

        def get_from_page(page_bs):
            table = _table_with_id(page_bs, 'cphBody_gvP')

            if not table:
                return []

            ret_res_set = []
            set_ind = -1

            for row in table.find_all('tr'):
                cells = list(map(lambda c: c.get_text().replace(u'\xa0', ' ').strip(), row.find_all('td')))
                if len(cells) < 5:
                    if set_ind < 0 or ret_res_set[set_ind].has_result_rows:
                        ret_res_set.append(RbScrapeResult())
                        set_ind += 1
                    ret_res_set[set_ind].add_tag('/'.join(cells))
                    continue
                if not ret_res_set[set_ind].has_col_map:
                    coldict = {k : i for k, i in zip(cells, itertools.count()) if RbScrapeEvent.COL_PAT.match(k)}
                    if len(coldict) >= 5:
                        ret_res_set[set_ind].add_col_map(coldict)
                    continue
                ret_res_set[set_ind].add_result_row(cells)

            return ret_res_set
        
        page1_list = get_from_page(bs)
        if not page1_list:
            return page1_list

        page_links = get_page_links()

        if not page_links:
            return page1_list

        # flattening
        try:
            more_pages = [p for res_list in \
                    map(lambda l: get_from_page(self.bs_for_url(urlp.urljoin(RbScrape.BASE_URL, l))), page_links) \
                    for p in res_list]
        except RequestException:
            logger.error('Page url didn''t work')
            return page1_list

        if not more_pages:
            return page1_list

        def merge(result, pages):
            '''
            consumes pages adding to result until not compatible (diff tags or columns)
            '''
            while pages:
                p = pages.pop(0)
                if p.tags == result.tags and p.col_map == result.col_map:
                    result.add_from_result(p)
                else:
                    break

        while True:
            merge(page1_list[len(page1_list) - 1], more_pages)
            if not more_pages:
                break
            page1_list.append(more_pages[0])

        self.cached_result_set = page1_list
        return self.cached_result_set


class RbScrapeResult(object):
    def __init__(self):
        self.tags = []
        self.col_map = {}
        self.result_rows = []

    def add_tag(self, tag):
        if tag:
            self.tags.append(tag)

    @property
    def has_col_map(self):
        return bool(self.col_map)

    def add_col_map(self, col_map):
        self.col_map = col_map

    @property
    def has_result_rows(self):
        return bool(self.result_rows)

    @property
    def result_columns(self):
        return self.col_map.keys()

    def add_result_row(self, row):
        if len(row) < len(self.col_map):
            return
        self.result_rows.append([row[i] for c, i in self.col_map.items()])

    def row_as_dict(self, n):
        return {col : res for col, res in zip(self.col_map.keys(), self.result_rows[n])}

    def add_from_result(self, result):
        self.result_rows += result.result_rows
    
