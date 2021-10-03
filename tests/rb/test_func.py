from unittest import TestCase
from pmgsavvsie.modules.rb import flatten_sets, dist_from_tag

class MockEvent(object):
    def __init__(self, tags, result_columns, result_rows):
        self.tags = tags
        self.result_columns = result_columns
        self.result_rows = result_rows

class MockEventSet(object):
    def __init__(self, date, name, type, event_url, result_url, result_set):
        self.date = date
        self.name = name
        self.type = type
        self.event_url = event_url
        self.result_url = result_url
        self._result_set = result_set

    def get_result_set(self):
        return self._result_set

class FuncTests(TestCase):
    def test_flatten_simple(self):
        sets = [MockEventSet('date1', 'name1', 'type1', 'eurl1', 'rurl1', [MockEvent(['tag1'], ['a1', 'b1', 'c1'], [['1', '2', '3']])]),
                MockEventSet('date2', 'name2', 'type2', 'eurl2', 'rurl2', [MockEvent(['tag2','tag22'], ['a2', 'b2', 'c2'], ['1', '2', '3'])])]

        flattened = list(flatten_sets(sets))

        self.assertEqual(len(flattened), 2)
        self.assertEqual(flattened[0].date, 'date1')
        self.assertEqual(flattened[0].name, 'name1 - tag1')
        self.assertEqual(flattened[0].label, 'type1')
        self.assertEqual(flattened[0].event_url, 'eurl1')
        self.assertEqual(flattened[0].result_url, 'rurl1')
        self.assertEqual(flattened[0].results_columns, ['a1', 'b1', 'c1'])
        self.assertEqual(flattened[0].results, [['1', '2', '3']])
        self.assertEqual(flattened[1].date, 'date2')
        self.assertEqual(flattened[1].name, 'name2 - tag2/tag22')
        self.assertEqual(flattened[1].label, 'type2')
        self.assertEqual(flattened[1].event_url, 'eurl2')
        self.assertEqual(flattened[1].result_url, 'rurl2')
        self.assertEqual(flattened[0].results_columns, ['a2', 'b2', 'c2'])
        self.assertEqual(flattened[0].results, [['1', '2', '3']])

    def test_flatten_simple(self):
        sets = [
                MockEventSet('date1', 'name1', 'type1', 'eurl1', 'rurl1', [
                    MockEvent(['tag1'], ['a1_1', 'b1_1', 'c1_1'], [['1', '2', '3']]),
                    MockEvent(['tag2'], ['a1_2', 'b1_2', 'c1_2'], [['1', '2', '3']]),
                    MockEvent(['tag3'], ['a1_3', 'b1_3', 'c1_3'], [['1', '2', '3']]),
                    ]),
                MockEventSet('date2', 'name2', 'type2', 'eurl2', 'rurl2', [
                    MockEvent(['tag2','tag22'], ['a2', 'b2', 'c2'], [['1', '2', '3']]),
                    ])]

        flattened = list(flatten_sets(sets))

        self.assertEqual(len(flattened), 4)
        self.assertEqual(flattened[0].date, 'date1')
        self.assertEqual(flattened[0].name, 'name1 - tag1')
        self.assertEqual(flattened[0].label, 'type1')
        self.assertEqual(flattened[0].event_url, 'eurl1')
        self.assertEqual(flattened[0].result_url, 'rurl1')
        self.assertEqual(flattened[0].results_columns, ['a1_1', 'b1_1', 'c1_1'])
        self.assertEqual(flattened[0].results, [['1', '2', '3']])
        self.assertEqual(flattened[1].date, 'date1')
        self.assertEqual(flattened[1].name, 'name1 - tag2')
        self.assertEqual(flattened[1].label, 'type1')
        self.assertEqual(flattened[1].event_url, 'eurl1')
        self.assertEqual(flattened[1].result_url, 'rurl1')
        self.assertEqual(flattened[1].results_columns, ['a1_2', 'b1_2', 'c1_2'])
        self.assertEqual(flattened[1].results, [['1', '2', '3']])
        self.assertEqual(flattened[2].date, 'date1')
        self.assertEqual(flattened[2].name, 'name1 - tag3')
        self.assertEqual(flattened[2].label, 'type1')
        self.assertEqual(flattened[2].event_url, 'eurl1')
        self.assertEqual(flattened[2].result_url, 'rurl1')
        self.assertEqual(flattened[2].results_columns, ['a1_3', 'b1_3', 'c1_3'])
        self.assertEqual(flattened[2].results, [['1', '2', '3']])
        self.assertEqual(flattened[3].date, 'date2')
        self.assertEqual(flattened[3].name, 'name2 - tag2/tag22')
        self.assertEqual(flattened[3].label, 'type2')
        self.assertEqual(flattened[3].event_url, 'eurl2')
        self.assertEqual(flattened[3].result_url, 'rurl2')
        self.assertEqual(flattened[3].results_columns, ['a2', 'b2', 'c2'])
        self.assertEqual(flattened[3].results, [['1', '2', '3']])

    def test_tag_to_dist(self):
        self.assertEqual(dist_from_tag('5.1KXC U20M'), '5.1KXC')
        self.assertEqual(dist_from_tag('parkrun'), 'parkrun')
        self.assertEqual(dist_from_tag('800 SW (23 Jan)'), '800')
        self.assertEqual(dist_from_tag('Mile SW (23 Jan)'), 'Mile')
