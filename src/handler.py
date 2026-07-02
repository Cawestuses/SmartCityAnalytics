from pathlib import Path

import numpy as np
from pandas import DataFrame, read_csv, concat
from pandas.errors import EmptyDataError
from misc.converter import date_to_str, str_to_date
from misc.settings import *

class Handler:
    def __init__(self):
        try:
            self.base_dir = Path(__file__).resolve().parent.parent
        except NameError:
            self.base_dir = Path.cwd()

        self.data_path = self.base_dir / "data"
        self.folders = {
            "report": "reports",
            "day":"reports",
            "month":"monthly",
            "year":"yearly",
            "rankings": "exports",
            "anomalies": "exports",
            "final_data": "exports"
        }

    def _check_for_file(self, date: str|int|tuple[int, int]|tuple[int, int, int]) -> bool:
        if isinstance(date, tuple):
            if len(date) == 3:
                date = date_to_str(*date)
            elif len(date) == 2:
                date = date_to_str(None, *date)
        elif isinstance(date, int):
            date = date_to_str(None, None, date)
        file_path = f"{date}.csv"

        if len(date) == 4:
            file_path = self.data_path / self.folders["year"] / file_path
        elif len(date) == 7:
            file_path = self.data_path / self.folders["month"] / file_path
        else:
            file_path = self.data_path / self.folders["day"] / file_path

        if file_path.is_file():
            return True
        else:
            return False

    def _create_sample_df(self, category: str, date:str|int|tuple[int, int]|None):
        dates = np.arange(1, 13)
        zeros = np.zeros((12, len(STATS)))

        if category == "month":
            dates = np.arange(1, 31)
            zeros = np.zeros((30, len(STATS)))

        df = DataFrame(zeros, index=dates, columns=STATS)
        df.index.name = "Date"
        self._save_csv(df, category, date)

    def _build_path(self, category:str, date: str|int|tuple[int,int]|tuple[int, int, int]|None = None) -> str:
        if isinstance(date, tuple):
            if len(date) == 3:
                date = date_to_str(*date)
            else:
                date = date_to_str(None, *date)
        elif isinstance(date, int):
            date = date_to_str(None, None, date)

        if category not in ["rankings", "anomalies", "final_data"]:
            full_path = self.data_path / self.folders[category] / f"{date}.csv"
        else:
            full_path = self.data_path / self.folders[category] / f"{category}.csv"

        return full_path

    def _load_csv(self, category:str, date: str|int|tuple[int,int]|tuple[int, int, int]|None = None) -> DataFrame:
        path = self._build_path(category, date)
        try:
            df = read_csv(path)
            print(f"{category} has loaded")
            return df
        except EmptyDataError:
            if category in ["anomalies", "rankings"]:
                print(f"There was no {category} statistics")
                return DataFrame()
            else:
                print(f"There was no {category} statistics in this date: {date}")
                self._create_sample_df(category, date)
                if self._check_for_file(date):
                    print("Created a sample csv")
                    return self._load_csv(category, date)
                else:
                    return DataFrame()

    def _save_csv(self, data: DataFrame, category:str, date: str|int|tuple[int,int]|tuple[int, int, int]|None = None):
        path = self._build_path(category, date)
        data.to_csv(path, index=False)
        print(f"{category} has saved")

    def add_day(self, data: DataFrame, date: str|tuple[int, int, int]):
        if data.empty:
            raise EmptyDataError
        if isinstance(date, str):
            day, month, year = str_to_date(date)
        else:
            day, month, year = date

        month_df = self._load_csv("month", date)
        month_df = concat([month_df, data], ignore_index=True)
        self._save_csv(month_df, "month", date)

    def add_month(self, data: DataFrame, date: str|tuple[int, int]):
        if data.empty:
            raise EmptyDataError
        if isinstance(date, str):
            month, year = str_to_date(date)
        else:
            month, year = date

        mp = data.iloc[0].to_dict()
        year_df = self._load_csv("year", year)
        year_df.loc[month] = mp
        self._save_csv(year_df, "year", date)

    def add_anomaly(self, data: DataFrame, date: str | tuple[int, int, int]):
        if data.empty:
            raise EmptyDataError
        mp = data.iloc[0].to_dict()
        anomalies_df = self._load_csv(category="anomalies")
        if isinstance(date, tuple):
            date = date_to_str(*date)
        anomalies_df[date] = mp
        self._save_csv(anomalies_df, category="anomalies")