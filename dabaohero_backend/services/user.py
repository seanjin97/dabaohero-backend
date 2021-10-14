import requests
from urllib.parse import urlencode, quote_plus
from dabaohero_backend import config
from dabaohero_backend.dao import users


# Retrieve Auth0 user object
def retrieve_auth0_user(email):
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

    res = requests.get(url, headers=headers).json()[0]

    return res


# Retrieve user object by username
def get_user(username):
    try:
        user = users.get_user(username)
        return user
    except Exception as e:
        print("services.user.get_user:", e)


# Create user by username
def create_user(username):
    user_object = {
        "key": username,
        "completed_orders": 0,
        "orders_requested": 0,
        "rating": 0,
        "active_sessions": []
    }
    try:
        user = users.create_user(user_object)
        return user
    except Exception as e:
        print("services.user.create_user:", e)


# Update user with new user object
def update_user(user_object):
    try:
        updated_user_object = users.update_user(user_object)
        return updated_user_object
    except Exception as e:
        print("services.user.update_user:", e)
