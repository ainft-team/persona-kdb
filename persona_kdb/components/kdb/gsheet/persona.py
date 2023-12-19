import os
from datetime import datetime
from typing import List, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

from components.kdb.gsheet.spreadsheet_utils import read_range, append_values

def get_persona_info(sheet_id) -> Dict:
    try:
        sheet_name = 'persona'
        sheet_range = f'{sheet_name}!A4:B15'
        fetched = read_range(sheet_id, sheet_range)
        ret = {}
        for elem in fetched:
            ret[elem[0]] = elem[1]
        return ret
    except IndexError as err:
        print(err, f"Please fill out all the values in the {sheet_name} spreadsheet")
    except HttpError as err:
        print(err)

def get_variable_keys(sheet_id, sheet_range=None) -> List[str]:
    try:
        sheet_name = 'persona'
        sheet_range = f'{sheet_name}!B2:B2' if sheet_range is None else f'{sheet_name}!{sheet_range}'
        fetched = read_range(sheet_id, sheet_range)[0][0].split(', ')
        return fetched
    except HttpError as err:
        print(err)

def get_persona_template(sheet_id, version='latest') -> str:
    try:
        sheet_name = 'persona'
        sheet_range = f'{sheet_name}!A18:B30'
        fetched = read_range(sheet_id, sheet_range)
        version_list = [_version for _version, prompt in fetched]
        if version in version_list:
            return fetched[version_list.index(version)][1]
    except HttpError as err:
        print(err)

def get_questionaire_template(sheet_id, version='latest') -> str:
    try:
        sheet_name = 'persona'
        sheet_range = f'{sheet_name}!C18:D30'
        fetched = read_range(sheet_id, sheet_range)
        version_list = [_version for _version, prompt in fetched]
        if version in version_list:
            return fetched[version_list.index(version)][1]
    except HttpError as err:
        print(err)
def get_evaluation_template(sheet_id, version='latest') -> str:
    try:
        sheet_name = 'persona'
        sheet_range = f'{sheet_name}!E18:F30'
        fetched = read_range(sheet_id, sheet_range)
        version_list = [_version for _version, prompt in fetched]
        if version in version_list:
            return fetched[version_list.index(version)][1]
    except HttpError as err:
        print(err)