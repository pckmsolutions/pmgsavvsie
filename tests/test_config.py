from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock
from pmgsavvsie.scrape import scrape_mod
from pmgsavvsie.util import get_dates
from pmgsavvsie import baseconfig
from datetime import datetime, timedelta
from itertools import count

class BaseConfig(baseconfig.BaseConfig):
    pass

def test_calls_with_correct_date_using_1day_range():
    class Config(BaseConfig):
        RANGE_START = '2020-03-01'
        RANGE_END = '2020-03-01'

    assert list(get_dates(Config(), None)) == _date_list('2020-03-01')

def test_calls_with_correct_date_using_nday_range():
    class Config(BaseConfig):
        RANGE_START = '2020-03-01'
        RANGE_END = '2020-03-04'

    assert list(get_dates(Config(), None)) == _date_list('2020-03-04', '2020-03-03', '2020-03-02', '2020-03-01')

@patch('pmgsavvsie.util.datetime')
def test_calls_with_correct_date_last_scrape(mock_dt):
    today = datetime(2020, 1, 12)
    today_m1 = today - timedelta(days=1)
    today_m2 = today - timedelta(days=2)

    mock_dt.utcnow = Mock(return_value=today)
    mock_dt.strptime = Mock(side_effect=datetime.strptime)

    class Config(BaseConfig):
        RESCRAPE_WINDOW = 0

    assert list(get_dates(Config(), today_m2.date())) == [today.date(), today_m1.date()]

@patch('pmgsavvsie.util.datetime')
def test_calls_with_correct_date_last_scrape_with_window(mock_dt):
    today = datetime(2020, 1, 12)
    days = [(today - timedelta(days=n)).date() for n in range(1,10)]

    mock_dt.utcnow = Mock(return_value=today)
    mock_dt.strptime = Mock(side_effect=datetime.strptime)

    class Config(BaseConfig):
        RESCRAPE_WINDOW = 5

    assert list(get_dates(Config(), today.date())) == [today.date()] + days[:5]

@patch('pmgsavvsie.util.datetime')
def test_limits_to_number_of_days(mock_dt):
    today = datetime(2020, 1, 12)
    days = [(today - timedelta(days=n)).date() for n in range(0,20)]

    mock_dt.utcnow = Mock(return_value=today)
    mock_dt.strptime = Mock(side_effect=datetime.strptime)

    class Config(BaseConfig):
        RESCRAPE_WINDOW = 0
        MAX_RANGE_LENGTH = 2

    assert list(get_dates(Config(), days[19])) == days[17:19]


def _date_list(*dates):
    return [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
