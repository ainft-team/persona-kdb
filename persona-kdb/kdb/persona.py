import os
import pandas as pd
from datetime import datetime
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS', os.getenv('CREDENTIAL_FILE'))
SHARED_DRIVE_ID = os.getenv('GOOGLE_SHARED_DRIVE_ID')
SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def _read_range(sheet_id, range_name):
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheet_id, range=range_name).execute()
    rows = result.get('values', [])
    print('{0} rows retrieved.'.format(rows))
    return rows

def get_persona_info(sheet_id) -> List[List[str]]:
    try:
        sheet_name = 'Persona'
        fetched = _read_range(sheet_id, f'{sheet_name}!B4:B11')
        return fetched
    except HttpError as err:
        print(err)
def get_persona_template(sheet_id, version='latest') -> str:
    try:
        #TODO(jakepyo): version에 따라서 template을 가져오도록 수정
        sheet_name = 'Persona'
        fetched = _read_range(sheet_id, f'{sheet_name}!B14')
        return fetched[0][0]
    except HttpError as err:
        print(err)
    
if __name__ == "__main__":
    get_persona_info(SPREADSHEET_ID)
    print(get_persona_template(SPREADSHEET_ID, 'latest'))