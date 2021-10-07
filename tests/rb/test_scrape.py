import pytest
from unittest import TestCase, mock
from pmgsavvsie.modules.rb import RbScrape, flatten_sets
import os
import datetime
from aiohttp import ClientError, ClientSession, ClientResponse, ClientResponseError, BasicAuth
from contextlib import asynccontextmanager

URLS = {
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=21-Oct-2019&dateto=4-Nov-2019&terraintypecodes=RMPTIX': 'races.html',
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=22-Oct-2019&dateto=3-Nov-2019&terraintypecodes=RMPTIX': 'races_paged.html',
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=23-Oct-2019&dateto=2-Nov-2019&terraintypecodes=RMPTIX': 'races_paged.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117': 'bushy_results.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328654': 'walesxc.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117x': 'bushy_results_p1.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117&pagenum=2': 'bushy_results_p2.html',
        }

RESP_JSON = '{"hello": 123}'
RESP_HEADERS = '{"Content-Type": "application/json"}'

class MockResp:
    def __init__(self, txt):
        self.text = txt

def mock_requests_get(client_session, url, **kwargs):
    if not url in URLS:
        raise ClientError('Not a real request excepition but url not in test map')

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), URLS[url])
    with open(filename, 'r') as f:
        return f.read()

@pytest.mark.asyncio
@pytest.fixture
async def rbscrape():
    with mock.patch('pmgsavvsie.util.client_session_get_text') as client_session_get_text:
        client_session_get_text.side_effect = mock_requests_get
        yield RbScrape(None, None)

@pytest.mark.asyncio
@pytest.mark.usefixtures('rbscrape')
async def test_gets_races(rbscrape):
    resp = await _get_event_sets_as_list(
            rbscrape, datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))
    assert len(resp) == 5

@pytest.mark.asyncio
@pytest.mark.usefixtures('rbscrape')
async def test_gets_event_result_sets(rbscrape):
    events = await _get_event_sets_as_list(rbscrape,
            datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))

    event0_result_set = await events[0].get_result_set()
    event1_result_set = await events[1].get_result_set()

    # expected count
    assert len(event0_result_set) == 1
    assert len(event1_result_set) == 2

    # expected tags
    assert len(event0_result_set[0].tags) == 1
    assert event0_result_set[0].tags[0] == 'parkrun'
    assert len(event1_result_set[0].tags) == 1
    assert event1_result_set[0].tags[0] == '5.1KXC U20M'
    assert len(event1_result_set[1].tags) == 1
    assert event1_result_set[1].tags[0] == '4.5KXC U15M'

    # expect row counts
    assert len(event0_result_set[0].result_rows) == 250
    assert len(event1_result_set[0].result_rows) == 134
    assert len(event1_result_set[1].result_rows) == 116

    # expected column maps
    assert event0_result_set[0].col_map == {
            'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 8, 'Club': 10, 'SB': 11, 'PB': 12, 'HC':13}
    assert event1_result_set[0].col_map == {
            'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 7, 'Club': 9, 'HC':10}
    assert event1_result_set[1].col_map == {
            'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 7, 'Club': 9, 'HC':10}

    def check_common(results1, results2):
        # expected random results
        assert results1(144) == \
                {'Pos': '145', 'Gun': '23:24', 'Name': 'Barry King', 'AG': 'V65', 'Club': 'Hercules Wimbledon',
                    'SB': '21:52', 'PB': '20:56', 'HC':'11.9'}

        assert results2(2) == \
                {'Pos': '3', 'Gun': '15:15', 'Name': 'Charlie Harris', 'AG': 'U15', 'Club': 'Swansea', 'HC':'1.2'}

    assert event0_result_set[0].row_as_dict(144) == \
            {'Pos': '145', 'Gun': '23:24', 'Name': 'Barry King', 'AG': 'V65', 'Club': 'Hercules Wimbledon',
                'SB': '21:52', 'PB': '20:56', 'HC':'11.9'}

    assert event1_result_set[1].row_as_dict(2) == \
            {'Pos': '3', 'Gun': '15:15', 'Name': 'Charlie Harris', 'AG': 'U15', 'Club': 'Swansea', 'HC':'1.2'}

    flattened = [f async for f in flatten_sets(async_sets([events[0], events[1]]))]
    assert len(flattened) == 3

    assert flattened[0].name == 'Bushy Park parkrun # 812 - parkrun'
    assert flattened[1].name == "South Wales Regional Schools' Boys Championships - 5.1KXC U20M"
    assert flattened[2].name == "South Wales Regional Schools' Boys Championships - 4.5KXC U15M"
    assert len(flattened[0].results) == 250
    assert flattened[0].category == 'run'
    assert flattened[0].distance == 'parkrun'
    assert len(flattened[1].results) == 134
    assert flattened[1].category == 'run'
    assert flattened[1].distance == '5.1KXC'
    assert len(flattened[2].results) == 116
    assert flattened[2].category == 'run'
    assert flattened[2].distance == '4.5KXC'

@pytest.mark.asyncio
async def test_gets_paged_event_results(rbscrape):
    events = await _get_event_sets_as_list(rbscrape, datetime.date(2019, 10, 22), datetime.date(2019, 11, 3))

    event0_result_set = await events[0].get_result_set()

    # expected count
    assert len(event0_result_set) == 1
    assert len(event0_result_set[0].tags) == 1
    assert event0_result_set[0].tags[0] == 'parkrun'
    assert len(event0_result_set[0].result_rows) == 6

    # expected column maps
    assert event0_result_set[0].col_map == \
            {'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 8, 'Club': 10, 'SB': 11, 'PB': 12, 'HC':13}


    # expected random results
    assert event0_result_set[0].row_as_dict(1) == \
            {'Pos': '2', 'Gun': '17:53', 'Name': 'Charlie Rowat', 'AG': 'S30', 'Club': 'Unattached',
                'SB': '', 'PB': '', 'HC':''}
    assert event0_result_set[0].row_as_dict(4) == \
            {'Pos': '253', 'Gun': '25:55', 'Name': 'Janet Livesey', 'AG': 'V45', 'Club': 'Stragglers/Thames Turbo',
                'SB': '23:34', 'PB': '23:26', 'HC':'14.9'}

async def xtest_gets_paged_event_results(rbscrape):
    # fix by testing bad url response
    #with self.assertRaises(RequestException):
    events = await _get_event_sets_as_list(rbscrape, datetime.date(2019, 10, 23), datetime.date(2019, 11, 2))
    event0 = events[0]

@pytest.mark.asyncio
async def test_gets_event_detail(rbscrape):
    def check_common(ev1, ev2):
        assert ev1.event_url == 'http://www.parkrun.org.uk/bushy/Results/WeeklyResults.aspx?runSeqNumber=812'
        assert ev1.date == 'Sat 26 Oct 2019'
        assert ev1.result_url == f'{RbScrape.BASE_URL}/results/results.aspx?meetingid=328117'
        assert ev2.event_url == 'https://www.thepowerof10.info/resultsfiles/2019/328654_7901_28102019105729.docx'
        assert ev2.date == 'Tue 22 Oct 2019'
        assert ev2.result_url == f'{RbScrape.BASE_URL}/results/results.aspx?meetingid=328654'

    events = await _get_event_sets_as_list(rbscrape, datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))

    check_common(events[0], events[1])
    assert events[0].name == 'Bushy Park parkrun # 812'
    assert events[0].type == 'parkrun'
    assert events[1].name == "South Wales Regional Schools' Boys Championships"
    assert events[1].type == 'XC'

    flattened = [f async for f in flatten_sets(async_sets([events[0], events[1]]))]

    check_common(flattened[0], flattened[1])
    assert flattened[0].name == 'Bushy Park parkrun # 812 - parkrun'
    assert flattened[0].label == 'parkrun'
    assert flattened[0].category == 'run'
    assert flattened[0].distance == 'parkrun'
    assert flattened[1].name == "South Wales Regional Schools' Boys Championships - 5.1KXC U20M"
    assert flattened[1].label == 'XC'
    assert flattened[1].category == 'run'
    assert flattened[1].distance == '5.1KXC'

async def _get_event_sets_as_list(scraper, date_from, date_to):
    return [_set async for _set in scraper.get_event_sets(date_from, date_to)]


async def async_sets(yield_sets):
    for s in yield_sets:
            yield s
