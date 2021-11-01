import uvicorn
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from services import user, session, api, postalcodes, leaderboard
import config
from fastapi_cloudauth.auth0 import Auth0
from models.user_dtos import LoginBodyDTO, RateUserDTO
from models.auth_dtos import AccessUser
from models.session_dtos import NewSessionDTO, SessionCodeDTO
from fastapi.responses import JSONResponse
import datetime
import pytz

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


# For frontend initial login
@app.post("/user/login", tags=["user"], description="Retrieve or creates user in Deta.")
def login(login_body: LoginBodyDTO,  AccessUser=Depends(auth.claim(AccessUser))):
    # Retrieve email from request body
    email = login_body.email

    # Retrieve user object from Auth0
    auth0_user = user.retrieve_auth0_user(email)

    # Retrieve user object from Deta, create new user if not created
    username = auth0_user["username"]

    deta_user = user.get_user(username)

    if not deta_user:
        deta_user = user.create_user(username)

    # Merge Auth0 & Deta user object
    merged_user = {**auth0_user, **deta_user}

    return merged_user


# Dabao-er creates new session
@app.post("/session/create", tags=["session"], description="Create a new session.")
def create_session(new_session_dto: NewSessionDTO, AccessUser=Depends(auth.claim(AccessUser))):

    # Check if user exists
    user_object = user.get_user(new_session_dto.username)
    if not user_object:
        return JSONResponse(status_code=400, content="Invalid user.")

    # Check if postal code is valid
    postal_code = new_session_dto.postal_code
    if len(postal_code) != 6:
        return JSONResponse(status_code=400, content="Invalid postal code.")
    try:
        float(postal_code)
    except ValueError:
        return JSONResponse(status_code=400, content="Invalid postal code.")

    # Get postal codes in the same postal sector (https://en.wikipedia.org/wiki/Postal_codes_in_Singapore)
    postal_group = postalcodes.get_postals_in_group(postal_code)

    # Error handling if invalid postal codes given
    if len(postal_group) == 0:
        return []

    # Verify that postal code is legit through API call
    origin = api.get_lat_long(postal_code)

    # Error handling for invalid postal_code
    if not origin:
        return JSONResponse(status_code=400, content="Invalid postal code.")

    # Create new session
    new_session = session.create_session(new_session_dto)

    updated_sessions = user_object["active_sessions"]
    updated_sessions.append(new_session["key"])
    user_object["active_sessions"] = updated_sessions
    updated_user_object = user.update_user(user_object)
    return updated_user_object


# Dabao-er completes a session
@app.post("/session/complete", tags=["session"], description="Complete a session.")
def complete_session(session_code_dto: SessionCodeDTO, AccessUser=Depends(auth.claim(AccessUser))):

    # Check if user exists
    user_object = user.get_user(session_code_dto.username)
    if not user_object:
        return JSONResponse(status_code=400, content="Invalid user.")

    current_sessions = user_object["active_sessions"]
    if not session_code_dto.session_code in current_sessions:
        return JSONResponse(status_code=400, content="The session for this session_code is not active for this user.")
    updated_sessions = [
        session for session in current_sessions if session != session_code_dto.session_code]
    user_object["active_sessions"] = updated_sessions

    updated_user_object = user.update_user(user_object)

    # Set session to inactive
    session_object = session.get_session(session_code_dto.session_code)
    if not session_object:
        return JSONResponse(status_code=400, content="The session does not exist.")

    session_object["is_active"] = False
    session.update_session(session_object)
    return updated_user_object


# List sessions by username
@app.get("/user/sessions/{username}", tags=["user"], description="List a user's sessions.")
def list_user_sessions(username, AccessUser=Depends(auth.claim(AccessUser))):
    user_object = user.get_user(username)
    if not user_object:
        return JSONResponse(status_code=400, content="Invalid user.")

    sessions = user_object["active_sessions"]
    session_details = []
    for i in sessions:
        retrieved_session = session.get_session(i)
        if retrieved_session:
            session_details.append(retrieved_session)

    return session_details


# Search for list of valid sessions based one postal code
@app.get("/session/search", tags=["session"], description="Retrieve available sessions to join based on postal code proximity")
def search_for_sessions(username: str = Query(...), postal_code: str = Query(..., min_length=6, max_length=6), AccessUser=Depends(auth.claim(AccessUser))):

    # Check if user exists
    user_object = user.get_user(username)
    if not user_object:
        return JSONResponse(status_code=400, content="Invalid user.")

    # Postal code validation
    try:
        float(postal_code)
    except ValueError:
        return JSONResponse(status_code=400, content="Invalid postal code.")

    # Get postal codes in the same postal sector (https://en.wikipedia.org/wiki/Postal_codes_in_Singapore)
    postal_group = postalcodes.get_postals_in_group(postal_code)

    # Error handling if invalid postal codes given
    if len(postal_group) == 0:
        return []

    # Shortlist potential sessions to reduce onemap api calls
    potential_sessions = []

    # Get current time
    tz = pytz.timezone("Asia/Singapore")
    current_time = int(datetime.datetime.now(tz).timestamp())

    # Filter by time and postal code prefix
    for postal in postal_group:
        potential_sessions += session.get_sessions_by_postal_prefix_and_time(
            postal, current_time, username)

    # Error handling if no existing sessions found
    if len(potential_sessions) == 0:
        return potential_sessions

    # Fine grained filtering to limit walking distance between source and origin to 500m
    origin = api.get_lat_long(postal_code)

    # Error handling for invalid postal_code
    if not origin:
        return []
    suitable_sessions = []
    for potential_session in potential_sessions:
        dest = api.get_lat_long(potential_session["postal_code"])

        # Error handling for invalid destination postal_code, skip to the next loop
        if not dest:
            continue

        distance = api.calculate_distance(origin, dest)
        if distance <= 500:
            suitable_sessions.append(potential_session)

    return suitable_sessions


# Join session
@app.post("/session/join", tags=["session"], description="Join session.")
def join_session(session_code_dto: SessionCodeDTO, AccessUser=Depends(auth.claim(AccessUser))):

    # Check if user exists
    user_object = user.get_user(session_code_dto.username)

    if not user_object:
        return JSONResponse(status_code=400, content="Invalid username.")

    # Retrieve existing session
    existing_session = session.get_session(session_code_dto.session_code)

    if not existing_session:
        return JSONResponse(status_code=400, content="Invalid session code.")

    # Add session to user object & update user object
    updated_sessions = user_object["active_sessions"]
    if session_code_dto.session_code in updated_sessions:
        return JSONResponse(status_code=400, content="User has already joined session.")

    updated_sessions.append(existing_session["key"])
    user_object["active_sessions"] = updated_sessions
    updated_user_object = user.update_user(user_object)

    # Add user as leecher to session & update session object
    leechers = existing_session["leechers"]
    leechers.append(session_code_dto.username)
    existing_session["leechers"] = leechers
    session.update_session(existing_session)

    return updated_user_object


# Rate session
@app.post("/user/rate", tags=["user"], description="Rate user")
def rate_user(rate_user_dto: RateUserDTO, AccessUser=Depends(auth.claim(AccessUser))):

    # Check if user exists
    user_object = user.get_user(rate_user_dto.username)
    if not user_object:
        return JSONResponse(status_code=400, content="Invalid username.")

    # Retrieve user to be rated
    user_to_rate_object = user.get_user(rate_user_dto.dabaoer)

    if not user_to_rate_object:
        return JSONResponse(status_code=400, content="Invalid dabaoer username.")

    rating = rate_user_dto.rating
    if (rating < 0 or rating > 5):
        return JSONResponse(status_code=400, content="Invalid rating given.")

    # Update number of completed orders
    curr_num_completed_orders = user_to_rate_object["completed_orders"]
    curr_num_completed_orders += 1
    user_to_rate_object["completed_orders"] = curr_num_completed_orders

    # Calculate new average rating https://stackoverflow.com/questions/28820904/how-to-efficiently-compute-average-on-the-fly-moving-average
    curr_average_rating = user_to_rate_object["rating"]
    new_average_rating = (1 / curr_num_completed_orders) * rating + \
        (1 - (1 / curr_num_completed_orders)) * curr_average_rating

    new_average_rating = round(new_average_rating, 2)
    user_to_rate_object["rating"] = new_average_rating
    user.update_user(user_to_rate_object)

    # Remove session from active session
    current_sessions = user_object["active_sessions"]
    if not rate_user_dto.session_code in current_sessions:
        return JSONResponse(status_code=400, content="The session for this session_code is not active for this user.")
    updated_sessions = [
        session for session in current_sessions if session != rate_user_dto.session_code]

    user_object["active_sessions"] = updated_sessions

    # Increment orders_requested
    curr_num_orders_requested = user_object["orders_requested"]
    curr_num_orders_requested += 1
    user_object["orders_requested"] = curr_num_orders_requested

    updated_user_object = user.update_user(user_object)
    return updated_user_object


# Get user profile
@app.get("/user/account/{email}", tags=["user"], description="Retrieve user profile.")
def get_user_profile(email, AccessUser=Depends(auth.claim(AccessUser))):
    auth0_user = user.retrieve_auth0_user(email)
    username = auth0_user["username"]

    user_object = user.get_user(username)
    merged_user = {**auth0_user, **user_object}
    return merged_user


@app.get("/leaderboard", tags=["leaderboard"], description="Retrieve leaderboard.")
def retrieve_leaderboard(AccessUser=Depends(auth.claim(AccessUser))):
    return leaderboard.leaderboard_top_10()


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
