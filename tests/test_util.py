from unittest import TestCase
from pmgsavvsie.core import ResultRow
from pmgsavvsie.util import cvt_to_result_row

class UtilTestCase(TestCase):

    def test_cvt_to_dict(self):
        converter = cvt_to_result_row(['Pos', 'Gun', 'Name', 'Club', 'AG', 'Gen'])

        converted = converter(['1', '12:11', 'Troy', 'Clubsie', '40+', 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))

        converted = converter(['1', '12:11', 'Troy', 'Clubsie', None, 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', None, 'M'))

    def test_cvt_to_dict_missing_fields(self):
        converter = cvt_to_result_row(['Pos', 'Gun', 'Name', 'x', 'y', 'z'])

        converted = converter(['1', '12:11', 'Troy', 'Clubsie', '40+', 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', None, None, None))

        converted = converter(['1', '12:11', 'Troy', 'Clubsie', None, 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', None, None, None))

    def test_cvt_to_dict_column_variations(self):
        converter = cvt_to_result_row(['pos', 'time', 'Name', 'Club', 'AG', 'Gen'])
        converted = converter(['1', '12:11', 'Troy', 'Clubsie', '40+', 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))

        converter = cvt_to_result_row(['Pos', 'Gun', 'Name', 'Club', 'Age Group', 'gender'])
        converted = converter(['1', '12:11', 'Troy', 'Clubsie', '40+', 'M'])
        self.assertEqual(converted, ResultRow.from_tup('1', '12:11', 'Troy', 'Clubsie', '40+', 'M'))



