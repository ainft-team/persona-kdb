from os import getenv
from dotenv import load_dotenv, find_dotenv
from typing import List, Optional
load_dotenv(find_dotenv('.env'))

from components.kdb.gsheet.spreadsheet_utils import read_range, append_values

def fetch_knowledge_base() -> List[List[str]]:
    """
    Fetches the knowledge base from the database and returns it as a list of
    dictionaries.

    Returns:
        list: A list of dictionaries containing the knowledge base.
    """
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
    sheet_name = "trainable_data"
    target_col = "C"

    raw_data = read_range(sheet_id, f"{sheet_name}!{target_col}:{target_col}")
    return raw_data

def append_knowledge(content: str):
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
    sheet_name = "trainable_data"
    target_col = "C"
    
    try:
        _values = [['threadId', 'knowledge', content]] # The row is appended from the first column value
        result = append_values(
            sheet_id=sheet_id,
            range_name=f"{sheet_name}!{target_col}:D",
            value_input_option="RAW",
            _values=_values,
        )
        return result is not None
    except Exception as e:
        print(e)
        return False
def append_conversation(conversation_id):
    #TODO
    # 1. fetch the conversation history from using conversation_id(=root message id)
    # 2. append the conversation history to the spreadsheet
    # 3. return the result
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
    sheet_name = "trainable_data"
    target_col = "C"

    #TODO: implement fetch_conversation_history
    conversation = "notimplemented"
    # conversation = fetch_conversation_history(conversation_id)
    
    try:
        _values = [['threadId', 'conversation', conversation]] # The row is appended from the first column value
        result = append_values(
            sheet_id=sheet_id,
            range_name=f"{sheet_name}!{target_col}:D",
            value_input_option="RAW",
            _values=_values,
        )
        return result is not None
    except Exception as e:
        print(e)
        return False
def update_vectordb():
    #TODO
    # 1. fetch the knowledge base from the spreadsheet
    # 2. update the vectordb using the knowledge base
    # 3. return the result
    return NotImplementedError

if __name__ == "__main__":
    fetch_knowledge_base()