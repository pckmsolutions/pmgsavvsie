from unittest import TestCase, mock
from pmgsavvsie.modules.rb import RbScrape, flatten_sets
import os
import datetime
from requests.exceptions import RequestException

URLS = {
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=21-Oct-2019&dateto=4-Nov-2019&terraintypecodes=RMPTIX': 'races.html',
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=22-Oct-2019&dateto=3-Nov-2019&terraintypecodes=RMPTIX': 'races_paged.html',
        'https://www.runbritainrankings.com/results/resultslookup.aspx?datefrom=23-Oct-2019&dateto=2-Nov-2019&terraintypecodes=RMPTIX': 'races_paged.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117': 'bushy_results.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328654': 'walesxc.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117x': 'bushy_results_p1.html',
        'https://www.runbritainrankings.com/results/results.aspx?meetingid=328117&pagenum=2': 'bushy_results_p2.html',
        }

class MockResp:
    def __init__(self, txt):
        self.text = txt

def mock_requests_get(url, **kwargs):
    if not url in URLS:
        raise RequestException('Not a real request excepition but url not in test map')

    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), URLS[url])
    with open(filename, 'r') as f:
        return MockResp(f.read())

class RbScrapeTests(TestCase):
    def setUp(self):
        requests_get_patcher = mock.patch('requests.get')
        self.mock_requests_get = requests_get_patcher.start()
        self.mock_requests_get.side_effect = mock_requests_get
        self.scraper = RbScrape(None)

    def tearDown(self):
        mock.patch.stopall()

    def test_gets_races(self):
        self.assertEqual(len(self.scraper.get_event_sets_as_list(datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))), 5)

    def test_gets_event_detail(self):
        def check_common(ev1, ev2):
            self.assertEqual(ev1.event_url, 'http://www.parkrun.org.uk/bushy/Results/WeeklyResults.aspx?runSeqNumber=812')
            self.assertEqual(ev1.date, 'Sat 26 Oct 2019')
            self.assertEqual(ev1.result_url, f'{RbScrape.BASE_URL}/results/results.aspx?meetingid=328117')
            self.assertEqual(ev2.event_url, 'https://www.thepowerof10.info/resultsfiles/2019/328654_7901_28102019105729.docx')
            self.assertEqual(ev2.date, 'Tue 22 Oct 2019')
            self.assertEqual(ev2.result_url, f'{RbScrape.BASE_URL}/results/results.aspx?meetingid=328654')

        events = self.scraper.get_event_sets_as_list(datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))

        check_common(events[0], events[1])
        self.assertEqual(events[0].name, 'Bushy Park parkrun # 812')
        self.assertEqual(events[0].type, 'parkrun')
        self.assertEqual(events[1].name, "South Wales Regional Schools' Boys Championships")
        self.assertEqual(events[1].type, 'XC')

        flattened = list(flatten_sets([events[0], events[1]]))

        check_common(flattened[0], flattened[1])
        self.assertEqual(flattened[0].name, 'Bushy Park parkrun # 812 - parkrun')
        self.assertEqual(flattened[0].label, 'parkrun')
        self.assertEqual(flattened[0].category, 'run')
        self.assertEqual(flattened[0].distance, 'parkrun')
        self.assertEqual(flattened[1].name, "South Wales Regional Schools' Boys Championships - 5.1KXC U20M")
        self.assertEqual(flattened[1].label, 'XC')
        self.assertEqual(flattened[1].category, 'run')
        self.assertEqual(flattened[1].distance, '5.1KXC')

    def test_gets_event_result_sets(self):
        rbscrape = RbScrape(None)
        events = self.scraper.get_event_sets_as_list(datetime.date(2019, 10, 21), datetime.date(2019, 11, 4))

        event0_result_set = events[0].get_result_set()
        event1_result_set = events[1].get_result_set()

        # expected count
        self.assertEqual(len(event0_result_set), 1)
        self.assertEqual(len(event1_result_set), 2)

        # expected tags
        self.assertEqual(len(event0_result_set[0].tags), 1)
        self.assertEqual(event0_result_set[0].tags[0], 'parkrun')
        self.assertEqual(len(event1_result_set[0].tags), 1)
        self.assertEqual(event1_result_set[0].tags[0], '5.1KXC U20M')
        self.assertEqual(len(event1_result_set[1].tags), 1)
        self.assertEqual(event1_result_set[1].tags[0], '4.5KXC U15M')

        # expect row counts
        self.assertEqual(len(event0_result_set[0].result_rows), 250)
        self.assertEqual(len(event1_result_set[0].result_rows), 134)
        self.assertEqual(len(event1_result_set[1].result_rows), 116)

        # expected column maps
        self.assertEqual(event0_result_set[0].col_map, \
                {'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 8, 'Club': 10, 'SB': 11, 'PB': 12, 'HC':13})
        self.assertEqual(event1_result_set[0].col_map, \
                {'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 7, 'Club': 9, 'HC':10})
        self.assertEqual(event1_result_set[1].col_map, \
                {'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 7, 'Club': 9, 'HC':10})

        def check_common(results1, results2):
            # expected random results
            self.assertEqual(results1(144), \
                    {'Pos': '145', 'Gun': '23:24', 'Name': 'Barry King', 'AG': 'V65', 'Club': 'Hercules Wimbledon',
                        'SB': '21:52', 'PB': '20:56', 'HC':'11.9'})

            self.assertEqual(results2(2), \
                    {'Pos': '3', 'Gun': '15:15', 'Name': 'Charlie Harris', 'AG': 'U15', 'Club': 'Swansea', 'HC':'1.2'})

        self.assertEqual(event0_result_set[0].row_as_dict(144), \
                {'Pos': '145', 'Gun': '23:24', 'Name': 'Barry King', 'AG': 'V65', 'Club': 'Hercules Wimbledon',
                    'SB': '21:52', 'PB': '20:56', 'HC':'11.9'})

        self.assertEqual(event1_result_set[1].row_as_dict(2), \
                {'Pos': '3', 'Gun': '15:15', 'Name': 'Charlie Harris', 'AG': 'U15', 'Club': 'Swansea', 'HC':'1.2'})

        flattened = list(flatten_sets([events[0], events[1]]))
        self.assertEqual(len(flattened), 3)

        self.assertEqual(flattened[0].name, 'Bushy Park parkrun # 812 - parkrun')
        self.assertEqual(flattened[1].name, "South Wales Regional Schools' Boys Championships - 5.1KXC U20M")
        self.assertEqual(flattened[2].name, "South Wales Regional Schools' Boys Championships - 4.5KXC U15M")
        self.assertEqual(len(flattened[0].results), 250)
        self.assertEqual(flattened[0].category, 'run')
        self.assertEqual(flattened[0].distance, 'parkrun')
        self.assertEqual(len(flattened[1].results), 134)
        self.assertEqual(flattened[1].category, 'run')
        self.assertEqual(flattened[1].distance, '5.1KXC')
        self.assertEqual(len(flattened[2].results), 116)
        self.assertEqual(flattened[2].category, 'run')
        self.assertEqual(flattened[2].distance, '4.5KXC')

    def test_gets_paged_event_results(self):
        rbscrape = RbScrape(None)
        events = self.scraper.get_event_sets_as_list(datetime.date(2019, 10, 22), datetime.date(2019, 11, 3))

        event0_result_set = events[0].get_result_set()

        # expected count
        self.assertEqual(len(event0_result_set), 1)
        self.assertEqual(len(event0_result_set[0].tags), 1)
        self.assertEqual(event0_result_set[0].tags[0], 'parkrun')
        self.assertEqual(len(event0_result_set[0].result_rows), 6)

        # expected column maps
        self.assertEqual(event0_result_set[0].col_map, \
                {'Pos': 1, 'Gun': 2, 'Name': 6, 'AG': 8, 'Club': 10, 'SB': 11, 'PB': 12, 'HC':13})


        # expected random results
        self.assertEqual(event0_result_set[0].row_as_dict(1), \
                {'Pos': '2', 'Gun': '17:53', 'Name': 'Charlie Rowat', 'AG': 'S30', 'Club': 'Unattached',
                    'SB': '', 'PB': '', 'HC':''})
        self.assertEqual(event0_result_set[0].row_as_dict(4), \
                {'Pos': '253', 'Gun': '25:55', 'Name': 'Janet Livesey', 'AG': 'V45', 'Club': 'Stragglers/Thames Turbo',
                    'SB': '23:34', 'PB': '23:26', 'HC':'14.9'})

    def xtest_gets_paged_event_results(self):
        # fix by testing bad url response
        #with self.assertRaises(RequestException):
        rbscrape = RbScrape(None)
        events = self.scraper.get_event_sets_as_list(datetime.date(2019, 10, 23), datetime.date(2019, 11, 2))
        event0 = events[0]



