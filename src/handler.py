import calendar
from datetime import date
from pathlib import Path
import numpy as np
from pandas import DataFrame, concat, read_csv
from pandas.errors import EmptyDataError
from misc.settings import STATS


class Handler:

    def __init__(self):
        try:
            self.base_dir = Path(__file__).resolve().parent.parent
        except NameError:
            self.base_dir = Path.cwd()

        self.data_path = self.base_dir / "data"
        self.folders = {
            "report": "reports",
            "day": "reports",
            "month": "monthly",
            "year": "yearly",
            "rankings": "exports",
            "anomalies": "exports",
            "final_data": "exports",
        }

    def _check_for_file(self, current_date: date, category: str) -> bool:
        try:
            file_path = self._build_path(category, current_date)
            return file_path.is_file()
        except FileNotFoundError:
            return False

    def _create_sample_df(self, category: str, current_date: date):
        if category == "year":
            dates = np.arange(1, 13)
            zeros = np.zeros((12, len(STATS)))
        elif category == "month":
            _, days_in_month = calendar.monthrange(
                current_date.year, current_date.month
            )
            dates = np.arange(1, days_in_month + 1)
            zeros = np.zeros((days_in_month, len(STATS)))
        else:
            dates = [current_date.day]
            zeros = np.zeros((1, len(STATS)))
        df = DataFrame(zeros, index=dates, columns=STATS)
        df.index.name = "Date"
        self._save_csv(df, category, current_date)

    def _build_path(self, category: str, current_date: date | None = None) -> Path:
        if category in ["rankings", "anomalies", "final_data"]:
            full_path = (
                self.data_path / self.folders[category] / f"{category}.csv"
            )
        else:
            if not isinstance(current_date, date):
                raise ValueError(
                    f"Для категории '{category}' необходим объект datetime.date"
                )
            if category == "year":
                file_name = current_date.strftime("%Y.csv")
            elif category == "month":
                file_name = current_date.strftime(
                    "%Y-%m.csv"
                )
            else:
                file_name = current_date.strftime(
                    "%Y-%m-%d.csv"
                )
            full_path = self.data_path / self.folders[category] / file_name

        return full_path

    def _load_csv(self, category: str, current_date: date | None = None) -> DataFrame:
        try:
            path = self._build_path(category, current_date)
            use_index = category not in ["anomalies", "rankings", "final_data"]
            df = read_csv(path, index_col = "Date" if use_index else  None)
            print(f"{category} has loaded")
            return df
        except (FileNotFoundError, EmptyDataError):
            if category in ["anomalies", "rankings", "final_data"]:
                print(f"There was no {category} statistics")
                return DataFrame()
            else:
                print(
                    f"There was no {category} statistics for this date: {current_date}"
                )
                self._create_sample_df(category, current_date)
                return self._load_csv(category, current_date)

    def _save_csv(
        self, data: DataFrame, category: str, current_date: date | None = None
    ):
        path = self._build_path(category, current_date)
        use_index = category not in ["anomalies", "rankings", "final_data"]
        data.to_csv(path, index=use_index)
        print(f"{category} has saved")

    def add_day(self, data: DataFrame, current_date: date):
        if data.empty:
            raise ValueError("DataFrame is empty")
        mp = data.iloc[0].to_dict()
        month_df = self._load_csv("month", current_date)
        month_df.loc[current_date.day] = mp
        self._save_csv(month_df, "month", current_date)

    def add_month(self, data: DataFrame, current_date: date):
        if data.empty:
            raise ValueError("DataFrame is empty")

        mp = data.iloc[0].to_dict()
        year_df = self._load_csv("year", current_date)
        year_df.loc[current_date.month] = mp
        self._save_csv(year_df, "year", current_date)

    def add_anomaly(self, data: DataFrame, current_date: date):
        if data.empty:
            raise ValueError("DataFrame is empty")

        anomalies_df = self._load_csv(category="anomalies")
        new_row = data.copy()
        new_row.insert(0, "date", current_date.strftime("%Y-%m-%d"))
        anomalies_df = concat([anomalies_df, new_row], ignore_index=True)

        self._save_csv(anomalies_df, category="anomalies")
