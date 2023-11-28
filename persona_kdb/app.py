from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes.v1 import v1_router

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
    uvicorn.run(app=app, host="0.0.0.0", port=5555, workers=1)