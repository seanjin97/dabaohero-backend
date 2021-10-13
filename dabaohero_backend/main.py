
import os
from requests.api import head
import uvicorn
from fastapi import FastAPI, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
import dao
import config
from fastapi_cloudauth.auth0 import Auth0, Auth0CurrentUser, Auth0Claims
from AccessTokenUser import AccessUser
import requests
from urllib.parse import urlencode, quote_plus
from pydantic import BaseModel

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


class LoginBody(BaseModel):
    email: str


@app.post("/login")
def login(login_body: LoginBody,  AccessUser=Depends(auth.claim(AccessUser))):
    # Retrieve email from request body
    email = login_body.email

    # Retrieve Auth0 API MGMT tokens
    client_id = config.MGMT_AUTH_CLIENT_ID
    client_secret = config.MGMT_AUTH_CLIENT_SECRET
    data = requests.post(f"{config.AUTH_URL}/oauth/token", {"grant_type": 'client_credentials',
                                                            "client_id": client_id,
                                                            "client_secret": client_secret,
                                                            "audience": f"{config.AUTH_URL}/api/v2/", })

    access_token, token_type = data.json()["access_token"], data.json()[
        "token_type"]

    # Retrieve user details from Auth0
    url = f"{config.AUTH_URL}/api/v2/users"
    email_param = f"email:{email}"
    params = urlencode(
        {"q": email_param, "search_engine": 'v3'}, quote_via=quote_plus)
    url += "?" + params
    headers = {"Authorization": f"{token_type} {access_token}"}
    res = requests.get(url, headers=headers)

    return res.json()[0]


@app.post("/user", status_code=201)
def create_user(username: str, AccessUser=Depends(auth.claim(AccessUser))):
    try:
        new_user = dao.create_user(username)
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
