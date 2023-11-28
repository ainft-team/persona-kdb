from os import getenv
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

from functools import lru_cache
import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1.client import Client

# Initialize Firebase
PROJECT_ROOT = Path(__file__).parent.parent
FIREBASE_CREDENTIALS_PATH = PROJECT_ROOT / getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS')
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

@lru_cache(maxsize=1)
def get_db() -> Client:
    return firestore.client()

class QueryPreset:
    @staticmethod
    def collection_list() -> str:
        c = get_db().collections()
        return [collection.id for collection in c]
    @staticmethod
    def get_conversation(conversation_id):
        try:
            c = get_db().collection("conversations").document(conversation_id).get()
            return c.to_dict()
        except Exception as e:
            print(e)
            return None
        
    def get_query_key(self) -> str:
        return list(self.query.keys())[0]

    def get_query_value(self) -> Any:
        return list(self.query.values())[0]