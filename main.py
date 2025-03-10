import os

from telethon.sync import TelegramClient
from message_generator import generate_message

api_id = os.environ["API_ID"]
api_hash = os.environ["API_HASH"]
dialog_id = os.environ["REPORTS_DIALOG_ID"]

with TelegramClient('name', api_id, api_hash) as client:
  client.send_message(int(dialog_id), generate_message())
