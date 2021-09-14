
import os
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cloudauth.auth0 import Auth0, Auth0CurrentUser, Auth0Claims

app = FastAPI(docs_url="/swagger")

# auth = Auth0(domain=os.environ["DOMAIN"], customAPI=os.environ["CUSTOMAPI"])

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
