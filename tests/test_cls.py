
from unittest import TestCase
from pmgsavvsie.core import ResultRow, KnownColumns

class ClsTestCase(TestCase):
    def test_result_row_equality(self):
        ''' this is really to be happy that comparison in unit tests works well '''
        self.assertEqual(ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertEqual(ResultRow.from_tup('1', None, 'Troy', 'Clubsie', '40+', 'M'),
                ResultRow.from_tup('1', None, 'Troy', 'Clubsie', '40+', 'M'))
        self.assertEqual(ResultRow.from_tup('1', '12:11', 'Troy', None, None, None),
                ResultRow.from_tup('1', '12:11', 'Troy', None, None, None))
        rr = ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M')
        self.assertEqual(rr,rr)
        self.assertNotEqual(ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('1', '12:11', 'Erik', 'Clubsie', '40+', 'M'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('2', '12:11', 'Troy', 'Clubsie', '40+', 'M'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('1', '12:11', 'Troy', 'Clubse', '40+', 'M'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '50+', 'f'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'm'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))
        self.assertNotEqual(ResultRow.from_tup('1', '12:11', None, 'Clubsie', '40+', 'm'),
                ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))

    def test_converts_to_dict(self):
        self.assertEqual(
                ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M').as_dict(KnownColumns),
                {
                    KnownColumns.POS.name.lower(): '1',
                    KnownColumns.TIME.name.lower(): '12:12',
                    KnownColumns.NAME.name.lower(): 'Troy',
                    KnownColumns.CLUB.name.lower(): 'Clubsie',
                    KnownColumns.AGE_GROUP.name.lower(): '40+',
                    KnownColumns.GENDER.name.lower(): 'M',
                    })

    def test_converts_to_filtered_dict(self):
        self.assertEqual(
                ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M').as_dict(
                    (KnownColumns.POS, KnownColumns.CLUB)),
                {
                    KnownColumns.POS.name.lower(): '1',
                    KnownColumns.CLUB.name.lower(): 'Clubsie',
                    })

    def test_convert_raises_value_error(self):
        with self.assertRaises(ValueError):
            ResultRow.from_tup('1', None, None, None, None, None).as_dict((KnownColumns.POS, KnownColumns.CLUB))

        with self.assertRaises(ValueError):
            ResultRow({
                KnownColumns.POS.name: '1',
                KnownColumns.NAME.name: 'name',
                KnownColumns.AGE_GROUP.name: 'age',
                KnownColumns.GENDER.name: 'gen',
                }).as_dict([KnownColumns.POS, KnownColumns.CLUB])

    def test_converts_to_with_optionals(self):
        self.assertEqual(
                ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M').as_dict(
                    [], (KnownColumns.POS, KnownColumns.CLUB)),
                {
                    KnownColumns.POS.name.lower(): '1',
                    KnownColumns.CLUB.name.lower(): 'Clubsie',
                    })

        self.assertEqual(
                ResultRow.from_tup('1', '12:12', 'Troy', 'Clubsie', '40+', 'M').as_dict(
                    (KnownColumns.NAME, ), (KnownColumns.POS, KnownColumns.CLUB)),
                {
                    KnownColumns.POS.name.lower(): '1',
                    KnownColumns.NAME.name.lower(): 'Troy',
                    KnownColumns.CLUB.name.lower(): 'Clubsie',
                    })

        self.assertEqual(
                ResultRow({
                    KnownColumns.CLUB.name: 'Clubsie',
                    }).as_dict([], [KnownColumns.POS, KnownColumns.NAME, KnownColumns.CLUB]),
                {
                    KnownColumns.CLUB.name.lower(): 'Clubsie',
                    })




