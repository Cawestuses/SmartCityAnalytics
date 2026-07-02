import unittest
from datetime import date
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
from src.handler import Handler


class TestHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.handler = Handler()
        # Изолируем тестовые данные в отдельную временную папку, чтобы не портить продакшн
        cls.test_dir = Path(__file__).resolve().parent.parent / "test_data"
        cls.test_dir.mkdir(exist_ok=True)

        # Подменяем пути у хендлера для безопасности тестов
        cls.handler.data_path = cls.test_dir
        for key in cls.handler.folders:
            cls.handler.folders[key] = "test_reports"
        (cls.test_dir / "test_reports").mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Полная очистка тестовой папки после прохождения всех тестов
        test_reports_dir = cls.test_dir / "test_reports"
        if test_reports_dir.exists():
            for file in test_reports_dir.iterdir():
                file.unlink()
            test_reports_dir.rmdir()
        if cls.test_dir.exists():
            cls.test_dir.rmdir()

    # ---------- Тесты _build_path с datetime.date ----------

    def test_build_day_path(self):
        test_date = date(2025, 6, 5)
        path = self.handler._build_path("day", test_date)
        self.assertEqual(path.name, "2025-06-05.csv")

    def test_build_month_path(self):
        test_date = date(2025, 6, 1)
        path = self.handler._build_path("month", test_date)
        self.assertEqual(path.name, "2025-06.csv")

    def test_build_year_path(self):
        test_date = date(2025, 1, 1)
        path = self.handler._build_path("year", test_date)
        self.assertEqual(path.name, "2025.csv")

    def test_build_anomalies_path(self):
        path = self.handler._build_path("anomalies")
        self.assertEqual(path.name, "anomalies.csv")

    # ---------- Тесты валидации типов (Граничные случаи) ----------

    def test_build_path_invalid_date_type(self):
        """Проверяем, что хендлер выбрасывает ValueError, если передана не datetime.date"""
        with self.assertRaises(ValueError):
            # Передаем старый кортеж вместо date
            self.handler._build_path("day", (5, 6, 2025))

    def test_add_day_empty_dataframe(self):
        """Проверяем, что метод add_day не падает с IndexError, а генерирует ValueError на пустой вход"""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            self.handler.add_day(empty_df, date(2025, 6, 5))

    # ---------- Тесты сохранения / загрузки цикла ----------

    def test_save_and_load_cycle(self):
        """Проверяем, корректно ли работает цикл записи и чтения данных"""
        test_date = date(2099, 1, 1)

        # Нам нужны колонки из настроек, чтобы имитировать реальные данные
        from misc.settings import STATS
        df = pd.DataFrame([[25.0] * len(STATS)], columns=STATS)

        self.handler._save_csv(df, "day", test_date)
        loaded_df = self.handler._load_csv("day", test_date)

        # Проверяем, совпадают ли загруженные данные с исходными
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_load_nonexistent_file_creates_sample(self):
        """Проверяем автосоздание пустого шаблона (sample), если файла нет на диске"""
        test_date = date(2026, 7, 2)
        # Файла на диске точно нет
        path = self.handler._build_path("month", test_date)
        if path.exists():
            path.unlink()

        df = self.handler._load_csv("month", test_date)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        # Индексом должны быть дни месяца
        self.assertEqual(df.index.name, "Date")


if __name__ == "__main__":
    unittest.main()