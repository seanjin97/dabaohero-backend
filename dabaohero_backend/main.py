
import os
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi_auth0 import Auth0, Auth0User
from dao import create_user
import config


auth = Auth0(domain=config.AUTH0_DOMAIN,
             api_audience=os.environ["AUTH0_API_AUDIENCE"])

app = FastAPI(docs_url="/swagger")

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


@app.get("/test")
async def root():
    return {"message": "test"}


@app.post("/user")
async def createUser(username: str):
    new_user = create_user(username)
    return new_user


@app.get("/public")
def get_public():
    return {"message": "Anonymous user"}


@app.get("/secure", dependencies=[Depends(auth.implicit_scheme)])
def get_secure():
    return {"message": "this is a private endpoint"}


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
