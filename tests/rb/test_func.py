import pytest
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

    async def get_result_set(self):
        return self._result_set

@pytest.mark.asyncio
async def test_flatten_simple_1():
    async def sets():
        yield_sets = [
                MockEventSet('date1', 'name1', 'type1', 'eurl1', 'rurl1', [
                    MockEvent(['tag1'], ['a1', 'b1', 'c1'], [['1', '2', '3']])]),
                MockEventSet('date2', 'name2', 'type2', 'eurl2', 'rurl2', [
                    MockEvent(['tag2','tag22'], ['a2', 'b2', 'c2'], [['1', '2', '3']])])]
        for s in yield_sets:
            yield s

    flattened = [f async for f in flatten_sets(sets())]

    assert len(flattened) == 2
    assert flattened[0].date == 'date1'
    assert flattened[0].name == 'name1 - tag1'
    assert flattened[0].label == 'type1'
    assert flattened[0].event_url == 'eurl1'
    assert flattened[0].result_url == 'rurl1'
    assert flattened[0].results_columns == ['a1', 'b1', 'c1']
    assert flattened[0].results == [['1', '2', '3']]
    assert flattened[1].date == 'date2'
    assert flattened[1].name == 'name2 - tag2/tag22'
    assert flattened[1].label == 'type2'
    assert flattened[1].event_url == 'eurl2'
    assert flattened[1].result_url == 'rurl2'
    assert flattened[1].results_columns == ['a2', 'b2', 'c2']
    assert flattened[1].results == [['1', '2', '3']]

@pytest.mark.asyncio
async def test_flatten_simple_2():
    async def sets():
        yield_sets = [
                MockEventSet('date1', 'name1', 'type1', 'eurl1', 'rurl1', [
                    MockEvent(['tag1'], ['a1_1', 'b1_1', 'c1_1'], [['1', '2', '3']]),
                    MockEvent(['tag2'], ['a1_2', 'b1_2', 'c1_2'], [['1', '2', '3']]),
                    MockEvent(['tag3'], ['a1_3', 'b1_3', 'c1_3'], [['1', '2', '3']]),
                    ]),
                MockEventSet('date2', 'name2', 'type2', 'eurl2', 'rurl2', [
                    MockEvent(['tag2','tag22'], ['a2', 'b2', 'c2'], [['1', '2', '3']]),
                    ])]
        for s in yield_sets:
            yield s

    flattened = [f async for f in flatten_sets(sets())]

    assert len(flattened) == 4
    assert flattened[0].date == 'date1'
    assert flattened[0].name == 'name1 - tag1'
    assert flattened[0].label == 'type1'
    assert flattened[0].event_url == 'eurl1'
    assert flattened[0].result_url == 'rurl1'
    assert flattened[0].results_columns == ['a1_1', 'b1_1', 'c1_1']
    assert flattened[0].results == [['1', '2', '3']]
    assert flattened[1].date == 'date1'
    assert flattened[1].name == 'name1 - tag2'
    assert flattened[1].label == 'type1'
    assert flattened[1].event_url == 'eurl1'
    assert flattened[1].result_url == 'rurl1'
    assert flattened[1].results_columns == ['a1_2', 'b1_2', 'c1_2']
    assert flattened[1].results == [['1', '2', '3']]
    assert flattened[2].date == 'date1'
    assert flattened[2].name == 'name1 - tag3'
    assert flattened[2].label == 'type1'
    assert flattened[2].event_url == 'eurl1'
    assert flattened[2].result_url == 'rurl1'
    assert flattened[2].results_columns == ['a1_3', 'b1_3', 'c1_3']
    assert flattened[2].results == [['1', '2', '3']]
    assert flattened[3].date == 'date2'
    assert flattened[3].name == 'name2 - tag2/tag22'
    assert flattened[3].label == 'type2'
    assert flattened[3].event_url == 'eurl2'
    assert flattened[3].result_url == 'rurl2'
    assert flattened[3].results_columns == ['a2', 'b2', 'c2']
    assert flattened[3].results == [['1', '2', '3']]

@pytest.mark.asyncio
async def test_tag_to_dist():
    assert dist_from_tag('5.1KXC U20M') == '5.1KXC'
    assert dist_from_tag('parkrun') == 'parkrun'
    assert dist_from_tag('800 SW (23 Jan)') == '800'
    assert dist_from_tag('Mile SW (23 Jan)') == 'Mile'
