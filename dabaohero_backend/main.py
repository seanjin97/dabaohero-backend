
import os
import uvicorn
from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from dao import create_user
import config
from fastapi_cloudauth.auth0 import Auth0, Auth0CurrentUser, Auth0Claims
from AccessTokenUser import AccessUser

auth = Auth0(domain=config.AUTH0_DOMAIN,
             customAPI=config.AUTH0_API_AUDIENCE)

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


@app.post("/user")
async def createUser(username: str, current_user: AccessUser = Depends(auth.claim(AccessUser))):
    try:
        new_user = create_user(username)
    except:
        return {"message": "user already exists"}

    return new_user


@app.get("/public")
def get_public():
    return {"message": "Anonymous user"}


@app.get("/access/")
def secure_access(current_user: AccessUser = Depends(auth.claim(AccessUser))):
    # access token is valid and getting user info from access token
    return f"Hello", {current_user.sub}


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
