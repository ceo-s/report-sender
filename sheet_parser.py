import pandas as pd
import numpy as np
import gspread
import json
import datetime

from typing import Callable
from functools import wraps


def _dt_from_excel_timestamp(xlsx_timestamp: int):
  if xlsx_timestamp is np.nan:
    return pd.NaT
  else:
    return datetime.datetime.fromtimestamp((int(xlsx_timestamp) - 25569) * 86400)


def fetch_sheet_data() -> pd.DataFrame:
  with open("creds.json") as file:
    credentials = json.load(file)

  gc = gspread.service_account_from_dict(credentials)
  worksheet = gc.open_by_key("1b_EkrUIZK6vgScuHpjLGYkj46V-gJpauFnU9hQObz7o").worksheet("Леша")
  df = pd.DataFrame(worksheet.get_all_records(value_render_option="UNFORMATTED_VALUE"))

  df = df[df["Задача"] != '']
  df = df[["Задача", "Плановая дата ", "Фактическая дата "]]
  df.columns = ["task", "date_plan", "date_fact"]
  df[df == ''] = np.nan

  df.date_plan = df.date_plan.apply(_dt_from_excel_timestamp).dt.normalize()
  df.date_fact = df.date_fact.apply(_dt_from_excel_timestamp).dt.normalize()
  return df.sort_values(["date_plan"])


def stringified(sep: str = ", "):

  def dec(func: Callable[[pd.DataFrame], pd.DataFrame]):

    @wraps(func)
    def wrapper(df: pd.DataFrame) -> list[str]:
      res = func(df)
      return [sep.join(map(str, row)) for row in res.itertuples(False, None)]

    return wrapper

  if isinstance(sep, Callable):
    func = sep
    sep = ", "
    return dec(func)

  return dec


@stringified
def get_todays_tasks(df: pd.DataFrame) -> pd.DataFrame:
  _today = datetime.date.today()
  return df.loc[df.date_fact.dt.date == _today, ["task", "date_fact"]]


@stringified
def get_done_tasks(df: pd.DataFrame) -> pd.DataFrame:
  _today = datetime.date.today()
  return df.loc[df.date_plan.dt.date < _today, ["task", "date_plan"]]


@stringified
def get_planned_tasks(df: pd.DataFrame) -> pd.DataFrame:
  _today = datetime.date.today()
  return df.loc[df.date_plan.dt.date > _today, ["task", "date_plan"]]
