import unittest
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError

# Исправь импорт на правильный, когда найдешь баг №5!
from src.handler import Handler


class TestHandlerEdgeCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.handler = Handler()
        # Используем тестовую директорию, чтобы не мусорить в боевой
        cls.test_dir = Path.cwd() / "test_data"
        cls.test_dir.mkdir(exist_ok=True)
        # Временно подменяем пути для изоляции тестов
        cls.handler.data_path = cls.test_dir
        cls.handler.folders = {k: "test_reports" for k in cls.handler.folders}
        (cls.handler.data_path / "test_reports").mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Очистка после тестов
        for file in (cls.handler.data_path / "test_reports").iterdir():
            file.unlink()
        (cls.handler.data_path / "test_reports").rmdir()
        cls.test_dir.rmdir()

    def test_load_empty_corrupted_csv(self):
        """Проверяем, что будет, если CSV файл физически существует, но пуст."""
        empty_file_path = self.handler._build_path("day", (15, 8, 2023))
        empty_file_path.touch()  # Создаем пустой файл 0 байт

        # Этот тест проверяет, что рекурсия (Ошибка №4) не уйдет в бесконечный цикл
        try:
            df = self.handler._load_csv("day", (15, 8, 2023))
            self.assertIsInstance(df, pd.DataFrame)
            self.assertFalse(df.empty)  # Должен создаться sample_df
        except RecursionError:
            self.fail("Обнаружена бесконечная рекурсия при обработке EmptyDataError!")

    def test_add_day_empty_dataframe_input(self):
        """Проверяем устойчивость к передаче пустого DataFrame в методы добавления."""
        empty_input_df = pd.DataFrame()

        # Ожидаем, что метод адекватно обработает пустой вход,
        # а не упадет с IndexError (Ошибка №3)
        with self.assertRaises((ValueError, IndexError)) as context:
            self.handler.add_day(empty_input_df, (15, 8, 2023))

        # Желательно, чтобы это была кастомная или понятная ошибка (ValueError),
        # а не системный IndexError от Pandas. Подумай над обработкой.