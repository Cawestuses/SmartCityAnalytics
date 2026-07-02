import unittest
from pathlib import Path

import pandas as pd

from misc.handler import Handler


class TestHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.handler = Handler()

    # ---------- _build_path ----------

    def test_build_day_path(self):
        path = self.handler._build_path("day", (5, 6, 2025))

        self.assertEqual(
            path.name,
            "05_06_2025.csv"
        )

    def test_build_month_path(self):
        path = self.handler._build_path("month", (6, 2025))

        self.assertEqual(
            path.name,
            "06_2025.csv"
        )

    def test_build_year_path(self):
        path = self.handler._build_path("year", 2025)

        self.assertEqual(
            path.name,
            "2025.csv"
        )

    def test_build_anomalies_path(self):
        path = self.handler._build_path("anomalies")

        self.assertEqual(
            path.name,
            "anomalies.csv"
        )

    # ---------- _check_for_file ----------

    def test_existing_report(self):
        self.assertTrue(
            self.handler._check_for_file((30, 7, 2010))
        )

    def test_missing_report(self):
        self.assertFalse(
            self.handler._check_for_file((1, 1, 1900))
        )

    # ---------- load csv ----------

    def test_load_anomalies(self):
        df = self.handler._load_csv("anomalies")

        self.assertIsInstance(
            df,
            pd.DataFrame
        )

    def test_load_rankings(self):
        df = self.handler._load_csv("rankings")

        self.assertIsInstance(
            df,
            pd.DataFrame
        )

    def test_load_final_data(self):
        df = self.handler._load_csv("final_data")

        self.assertIsInstance(
            df,
            pd.DataFrame
        )

    # ---------- save/load cycle ----------

    def test_save_and_load_temp_file(self):

        df = pd.DataFrame({
            "A": [1],
            "B": [2]
        })

        self.handler._save_csv(
            df,
            "day",
            (1, 1, 2099)
        )

        loaded = self.handler._load_csv(
            "day",
            (1, 1, 2099)
        )

        pd.testing.assert_frame_equal(
            df,
            loaded
        )

        temp = self.handler._build_path(
            "day",
            (1, 1, 2099)
        )

        if temp.exists():
            temp.unlink()

    # ---------- invalid ----------

    def test_invalid_category(self):
        with self.assertRaises(KeyError):
            self.handler._build_path("unknown")

    def test_return_type(self):
        path = self.handler._build_path(
            "day",
            (1, 1, 2025)
        )

        self.assertIsInstance(
            path,
            Path
        )


if __name__ == "__main__":
    unittest.main()