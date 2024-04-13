from os import getenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import argparse

from api.routes.v1 import v1_router
from api.routes.onepager import onepager_router
from api.scheduler import scheduling

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8102",
        "https://soulfiction-allinone.vercel.app",
        getenv("DISCORD_BOT_HOST")
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(v1_router)
app.include_router(onepager_router)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--update_vectordb', action='store_true', help='update vector database')
    args = parser.parse_args()
    if args.update_vectordb:
        scheduling()
    uvicorn.run(
        app=app, 
        host="0.0.0.0", 
        port=5555, 
        workers=1,
        ssl_keyfile=getenv("SSL_KEYFILE"),
        ssl_certfile=getenv("SSL_CERTFILE")
    )