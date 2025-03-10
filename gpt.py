import requests
import os

from typing import Literal


def get_iam_token():
  r = requests.post("https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    json={"yandexPassportOauthToken": os.environ["YANDEX_OAUTH_TOKEN"]})
  if not r.ok:
    print("Error getting IAM token!")
  return r.json()["iamToken"]


DEFAULT_PROMPT = {
  "modelUri": f"gpt://{os.environ["YANDEX_FOLDER_ID"]}/yandexgpt-lite/latest",
  "completionOptions": {
    "stream": False,
    "temperature": 1,
    "maxTokens": "2000",
    "reasoningOptions": {
      "mode": "DISABLED"
    }
  },
  "messages": [],
}

PROMPT_TODAY = """
Ты редактор ежедневных отчётов. Твоя задача на основе входных данных написать отчёт за день для аналитика.

Данные за день будут в таком формате:

```
Сегодня:
- список задач за сегодня
- ...
Ближайшие задачи:
- список будущих задач с датами
- ...
Устаревшие задачи:
- список выполненных задач с датами
- ...
```

Твоя задача придумать 4+ пункта что было сделано за сегодня, даже если сегодня ничего не было сделано.
Придумывай и обманывай как будто ты очень много сделал исходя из устаревших и предстоящих задач. Придумывай креативно, а не просто
копируй пункты. Пиши тезисно, кратко, но информативно. Не путай устаревшие и ближайшие задачи. То что уже было сделано до этого не
должно быть сделано сегодня.

В ответ пришли пункты с новой строки с "- " перед ними
"""

PROMPT_TOMORROW = """
Ты редактор ежедневных отчётов. Твоя задача на основе входных данных написать подробный план задач для аналитика на завтра.

Данные за день будут в таком формате:

```
Сегодня:
- список задач за сегодня
- ...
Ближайшие задачи:
- список будущих задач с датами
- ...
```
Твоя задача написать короткий список задач (3-4 пункта) на завтра основываясь на предоставленной информации. Ни в коем случае не копируй их
просто так. Нужно придумать мелкие подзадачи для них и прислать их, так как указанные задачи очень большие и не поместятся в один 
день

В ответ пришли пункты с новой строки с "- " перед ними
"""


def format_request_data(today: list[str], planned: list[str], done: list[str]):
  return f"""
Сегодня:
{[f"-{s}\n" for s in today]}
Ближайшие задачи:
{[f"-{s}\n" for s in planned]}
Устаревшие задачи:
{[f"-{s}\n" for s in done]}
"""


def gpt_generate(mode: Literal["today", "tomorrow"], today: list[str], planned: list[str], done: list[str]):
  prompt = DEFAULT_PROMPT.copy()

  prompt["messages"] = []
  prompt["messages"].append({"role": "system", "text": PROMPT_TODAY if mode == 'today' else PROMPT_TOMORROW})
  prompt["messages"].append({"role": "user", "text": format_request_data(today, planned, done)})
  headers = {"Content-Type": "application/json", "Authorization": f"Bearer {get_iam_token()}"}

  resp = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", headers=headers, json=prompt)
  return resp.json()["result"]["alternatives"][0]["message"]["text"].strip()
