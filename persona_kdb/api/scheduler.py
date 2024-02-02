from apscheduler.schedulers.background import BackgroundScheduler
from os import getenv
import logging
from datetime import datetime
import pinecone
import pytz
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
timezone = pytz.timezone("Asia/Seoul")

def update_vectordb():
    current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
    try:
        from components.kdb.gsheet.trainable_data import fetch_knowledge_base
        from components.core.vectordb import vdb_update
        #fetch knowledge base from gsheet
        docs = fetch_knowledge_base()
        # flush existing document
        pinecone.init(api_key=getenv("PINECONE_API_KEY"), 
                        environment=getenv("PINECONE_ENV", "northamerica-northeast1-gcp"))
        index = pinecone.Index(getenv("PINECONE_INDEX", "search-and-discovery"))
        index.delete(namespace=getenv("PINECONE_NAMESPACE"), delete_all=True)        
        vdb_update(docs=docs, chunk_size=200, chunk_overlap=0)
        logger.info(f"{current_time}: Successfully updated the vector database")
    except Exception as e:
        current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"{current_time}: Failed to update the vector database: {e}")

def scheduling():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_vectordb, 'cron', hour='*', minute=0, timezone='Asia/Seoul')
    scheduler.start()