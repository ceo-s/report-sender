import datetime
from sheet_parser import fetch_sheet_data, get_done_tasks, get_planned_tasks, get_todays_tasks
from gpt import gpt_generate


def get_next_val():
  _today = datetime.date.today()
  if _today.isoweekday() != 5:
    return "завтра"
  else:
    monday = _today + datetime.timedelta(3)
    return monday.strftime("%d.%m.%Y")


def generate_message():
  df = fetch_sheet_data()
  today = get_todays_tasks(df)
  planned = get_planned_tasks(df)
  done = get_done_tasks(df)

  return f"""
Отчёт за {datetime.date.today().strftime("%d.%m.%Y")}

Сегодня:
{gpt_generate("today", today, planned, done)}

Задачи на {get_next_val()}:
{gpt_generate("today", today, planned, [])}

#sokolov
"""
