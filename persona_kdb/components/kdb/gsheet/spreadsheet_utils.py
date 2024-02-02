from os import getenv
from datetime import datetime
from typing import List, Dict, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

from components.kdb.gsheet.types import ValueInputOption, MessageType, SpreadSheetRow

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
SERVICE_ACCOUNT_FILE = getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS')

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=creds)

def read_range(sheet_id, range_name):
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheet_id, range=range_name).execute()
    rows = result.get('values', [])
    return rows

def append_values(
        sheet_id: str, 
        range_name: str, 
        value_input_option: ValueInputOption, 
        _values: List[SpreadSheetRow]
    ):
    """
    Appends row(s) to a spreadsheet.
    
    Example -> append row
        append_values(
            sheet_id=SPREADSHEET_ID,
            range_name="chat_history!A:D",
            value_input_option=ValueInputOption.RAW,
            _values=[[now(), MessageType.HUMAN, "Hi Mars", now()], [...]]
        )
    """
    try:
        body = {"values": _values}
        result = (
            spreadsheet_service.spreadsheets()
            .values()
            .append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
    return error