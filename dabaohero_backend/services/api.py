import requests
from dabaohero_backend import config
import time
from urllib.parse import urlencode, quote_plus

ONEMAP_API_URL = config.ONEMAP_API
ONEMAP_EMAIL = config.ONEMAP_EMAIL
ONEMAP_PASSWORD = config.ONEMAP_PASSWORD
TOKEN_EXPIRATION_TIME = int(time.time())
TOKEN = ""


def get_onemap_token():
    global TOKEN_EXPIRATION_TIME
    global TOKEN
    # Reuse cached token if expiration time not yet reached, else regenerate new token and cache it
    if int(time.time()) >= TOKEN_EXPIRATION_TIME:
        body = {"email": ONEMAP_EMAIL, "password": ONEMAP_PASSWORD}
        res = requests.post(
            f"{ONEMAP_API_URL}/privateapi/auth/post/getToken", body).json()
        TOKEN = res["access_token"]
        TOKEN_EXPIRATION_TIME = int(res["expiry_timestamp"])


def get_lat_long(postal_code):
    res = requests.get(
        f"{ONEMAP_API_URL}/commonapi/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=N").json()["results"][0]
    return {"lat": res["LATITUDE"], "long": res["LONGITUDE"]}


def calculate_distance(origin, dest):
    get_onemap_token()
    url = f"{ONEMAP_API_URL}/privateapi/routingsvc/route?"
    params = urlencode(
        {
            "start": f"{origin['lat']},{origin['long']}",
            "end": f"{dest['lat']},{dest['long']}",
            "routeType": "walk",
            "token": TOKEN
        }, quote_via=quote_plus)
    url += params
    res = requests.get(url).json()
    total_distance = res["route_summary"]["total_distance"]
    return total_distance
