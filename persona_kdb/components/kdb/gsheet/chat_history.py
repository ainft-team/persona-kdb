from os import getenv
from datetime import datetime
from typing import List, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

from components.kdb.gsheet.spreadsheet_utils import read_range, append_values
# from kdb.types import ValueInputOption, MessageType, SpreadSheetRow

def get_recent_history(sheet_id, k=10):
    try:
        sheet_name = 'chat_history'
        fetched = read_range(sheet_id, f'{sheet_name}!A:D')
        return fetched
    except HttpError as err:
        print(err)
def get_kg(sheet_id):
    try:
        sheet_name = 'trainable_chat'
        fetched = read_range(sheet_id, f'{sheet_name}!A:C')
        ret = []
        for i, elem in enumerate(fetched):
            if i == 0:
                column_keys = elem
            else:
                elem = dict(zip(column_keys, elem))
                ret.append(elem)

        return ret
    except HttpError as err:
        print(err)