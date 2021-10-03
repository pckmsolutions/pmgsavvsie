from enum import Enum

class AbstractScraper(object):
    def scrape(self, date_from, date_to):
        ''' return list of AbstractEvents'''
        pass

class AbstractEvent(object):
    def __init__(self, **kwargs):
        self._date = kwargs.get('date')
        self._name = kwargs.get('name')
        self._label = kwargs.get('label')
        self._category = kwargs.get('category')
        self._distance = kwargs.get('distance')
        self._event_url = kwargs.get('event_url')
        self._result_url = kwargs.get('result_url')
        self._results_columns = kwargs.get('results_columns')
        self._results = kwargs.get('results')

    @property
    def date(self):
        return self._date

    @property
    def name(self):
        return self._name

    @property
    def label(self):
        return self._label

    @property
    def category(self):
        return self._category

    @property
    def distance(self):
        return self._distance

    @property
    def event_url(self):
        return self._event_url

    @property
    def result_url(self):
        return self._result_url

    @property
    def results_columns(self):
        ''' returns list of strings
        '''
        return self._results_columns

    @property
    def results(self):
        ''' returns list of tupples of length results_columns - a value for each
        '''
        return self._results

class KnownColumns(Enum):
    POS = ('Pos', 'pos', 'position')
    TIME = ('Gun', 'Time', 'gun', 'time')
    NAME = ('Name', 'name')
    CLUB = ('Club', 'club')
    AGE_GROUP = ('AG', 'ag', 'Ag', 'Age Group')
    GENDER = ('Gen', 'gen', 'Gender', 'gender')

class ResultRow(object):
    def __init__(self, coldict):
        self.coldict = {k:v for (k,v) in coldict.items() if v != None}

    @staticmethod
    def from_tup(pos, time, name, club, age_group, gender):
        return ResultRow({
                KnownColumns.POS.name: pos,
                KnownColumns.TIME.name: time,
                KnownColumns.NAME.name: name,
                KnownColumns.CLUB.name: club,
                KnownColumns.AGE_GROUP.name: age_group,
                KnownColumns.GENDER.name: gender,
                })

    @property
    def pos(self):
        return self.coldict.get(KnownColumns.POS.name)

    @property
    def time(self):
        return self.coldict.get(KnownColumns.TIME.name)

    @property
    def name(self):
        return self.coldict.get(KnownColumns.NAME.name)
    
    @property
    def club(self):
        return self.coldict.get(KnownColumns.CLUB.name)
    
    @property
    def age_group(self):
        return self.coldict.get(KnownColumns.AGE_GROUP.name)
    
    @property
    def gender(self):
        return self.coldict.get(KnownColumns.GENDER.name)

    def as_dict(self, required, optional=None):
        req = {k.lower():v for (k,v) in self.coldict.items() if k in [col.name for col in required]}
        if len(req) < len(required):
            missing = [col.name for col in required if not col in req.keys()]
            raise ValueError(f'{self.__class__.__name__} convert failed: missing columns {missing}')

        return req if not optional else {**req, **{k.lower():v for (k,v) in self.coldict.items() if k in [col.name for col in optional]}}

    def __eq__(self, other): 
        return isinstance(other, ResultRow) and (id(self) == id(other) or ResultRow._tup(self) == ResultRow._tup(other))

    @staticmethod
    def _tup(self):
        return (self.pos, self.time, self.name, self.club, self.age_group, self.gender)

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(ResultRow._tup(self))})'



