from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse

from api.routes.v1 import v1_router

parser = argparse.ArgumentParser()
parser.add_argument('--update_vectordb', action='store_true', help='update vector database')
args = parser.parse_args()

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )
app.include_router(v1_router)

if __name__ == "__main__":
    if args.update_vectordb:
        from os import getenv
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv('.env'))

        from components.kdb.gsheet.trainable_data import fetch_knowledge_base
        from components.core.vectordb import vdb_update
        import pinecone
        #fetch knowledge base from gsheet
        docs = fetch_knowledge_base()
        # flush existing document
        pinecone.init(api_key=getenv("PINECONE_API_KEY"), 
                      environment=getenv("PINECONE_ENV", "northamerica-northeast1-gcp"))
        index = pinecone.Index(getenv("PINECONE_INDEX", "search-and-discovery"))
        index.delete(namespace=getenv("PINECONE_NAMESPACE", "kdb_soulfiction"), delete_all=True)
        # update vector database
        vdb_update(docs=docs, chunk_size=200, chunk_overlap=0)
    uvicorn.run(app=app, host="0.0.0.0", port=5555, workers=1)