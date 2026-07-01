from pathlib import Path
from pandas import DataFrame, read_csv
from converter import date_to_str, str_to_date

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
        df = read_csv(path)
        print(f"{category} has loaded")
        return df

    def _save_csv(self, data: DataFrame, category:str, date: str|int|tuple[int,int]|tuple[int, int, int]|None = None):
        path = self._build_path(category, date)
        data.to_csv(path, index=False)
        print(f"{category} has saved")

    def add_day(self, data: DataFrame, date: str|tuple[int, int, int]):
        if isinstance(date, str):
            day, month, year = str_to_date(date)
        else:
            day, month, year = date

        mp = data.iloc[0].to_dict()
        month_df = self._load_csv("month", date)
        month_df.loc[day] = mp
        self._save_csv(month_df, "month", date)

    def add_month(self, data: DataFrame, date: str|tuple[int, int]):
        if isinstance(date, str):
            month, year = str_to_date(date)
        else:
            month, year = date

        mp = data.iloc[0].to_dict()
        year_df = self._load_csv("year", year)
        year_df.loc[month] = mp
        self._save_csv(year_df, "year", date)

    def add_anomaly(self, data: DataFrame, date: str | tuple[int, int, int]):
        mp = data.iloc[0].to_dict()
        anomalies_df = self._load_csv(category="anomalies")
        if isinstance(date, tuple):
            date = date_to_str(*date)
        anomalies_df[date] = mp
        self._save_csv(anomalies_df, category="anomalies")