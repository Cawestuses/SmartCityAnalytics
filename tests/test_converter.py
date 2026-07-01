import unittest

from src.converter import (
    valid_date,
    str_to_date,
    date_to_str
)


class TestValidDate(unittest.TestCase):

    def test_valid_year(self):
        self.assertTrue(valid_date(2025))

    def test_invalid_year(self):
        self.assertFalse(valid_date(-1))
        self.assertFalse(valid_date(5000))

    def test_valid_month(self):
        self.assertTrue(valid_date(2025, 6))

    def test_invalid_month(self):
        self.assertFalse(valid_date(2025, 0))
        self.assertFalse(valid_date(2025, 13))

    def test_valid_day(self):
        self.assertTrue(valid_date(2025, 6, 30))

    def test_invalid_day(self):
        self.assertFalse(valid_date(2025, 6, 0))
        self.assertFalse(valid_date(2025, 6, 32))


class TestDateToStr(unittest.TestCase):

    def test_year(self):
        self.assertEqual(
            date_to_str(None, None, 2025),
            "2025"
        )

    def test_month(self):
        self.assertEqual(
            date_to_str(None, 6, 2025),
            "06_2025"
        )

    def test_day(self):
        self.assertEqual(
            date_to_str(5, 6, 2025),
            "05_06_2025"
        )


class TestStrToDate(unittest.TestCase):

    def test_parse_year(self):
        self.assertEqual(
            str_to_date("2025"),
            2025
        )

    def test_parse_month(self):
        self.assertEqual(
            str_to_date("06_2025"),
            (6, 2025)
        )

    def test_parse_day(self):
        self.assertEqual(
            str_to_date("05_06_2025"),
            (5, 6, 2025)
        )

    def test_parse_with_symbols(self):
        self.assertEqual(
            str_to_date("05-06-2025"),
            (5, 6, 2025)
        )

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            str_to_date("abcdef")

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            str_to_date("12345")


if __name__ == "__main__":
    unittest.main()