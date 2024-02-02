from os import getenv
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

from functools import lru_cache
import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1.client import Client
# from google.cloud import firestore as firestore_for_async

# Initialize Firebase
PROJECT_ROOT = Path(__file__).parent.parent
FIREBASE_CREDENTIALS_PATH = PROJECT_ROOT / getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIALS')
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

@lru_cache(maxsize=1)
def get_db() -> Client:
    return firestore.client()

# async def get_async_db() -> firestore_for_async.AsyncClient:
#     return firestore_for_async.AsyncClient(project='ai-marketplace-394008')