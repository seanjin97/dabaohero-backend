import uvicorn
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dabaohero_backend.services import user, session, api, postalcodes
from dabaohero_backend import config
from fastapi_cloudauth.auth0 import Auth0
from dabaohero_backend.models.user_dtos import LoginBodyDTO, RateUserDTO
from dabaohero_backend.models.auth_dtos import AccessUser
from dabaohero_backend.models.session_dtos import NewSessionDTO, SessionCodeDTO
from fastapi.responses import JSONResponse


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
    # Check if postal code is valid
    postal_code = new_session_dto.postal_code
    if len(postal_code) != 6:
        return JSONResponse(status_code=400, content="Invalid postal code")
    try:
        float(postal_code)
    except ValueError:
        return JSONResponse(status_code=400, content="Invalid postal code")

    # Create new session
    new_session = session.create_session(new_session_dto)

    # Add session to user object & update user object
    user_object = user.get_user(new_session_dto.username)

    updated_sessions = user_object["active_sessions"]
    updated_sessions.append(new_session["key"])
    user_object["active_sessions"] = updated_sessions
    updated_user_object = user.update_user(user_object)
    return updated_user_object


# Dabao-er completes a session
@app.post("/session/complete", tags=["session"], description="Complete a session.")
def complete_session(session_code_dto: SessionCodeDTO, AccessUser=Depends(auth.claim(AccessUser))):
    # Remove session from user object
    user_object = user.get_user(session_code_dto.username)
    current_sessions = user_object["active_sessions"]
    if not session_code_dto.session_code in current_sessions:
        return JSONResponse(status_code=400, content="The session for this session_code is not active for this user.")
    updated_sessions = [
        session for session in current_sessions if session != session_code_dto.session_code]
    user_object["active_sessions"] = updated_sessions

    updated_user_object = user.update_user(user_object)

    # Set session to inactive
    session_object = session.get_session(session_code_dto.session_code)
    session_object["is_active"] = False
    session.update_session(session_object)
    return updated_user_object


# List sessions by username
@app.get("/user/sessions/{username}", tags=["user"], description="List a user's sessions.")
def list_user_sessions(username, AccessUser=Depends(auth.claim(AccessUser))):
    sessions = session.get_sessions_by_dabaoer(username)
    return sessions


# Search for list of valid sessions based one postal code
@app.get("/session/search", tags=["session"], description="Retrieve available sessions to join based on postal code proximity")
def search_for_sessions(postal_code: str = Query(..., min_length=6, max_length=6), AccessUser=Depends(auth.claim(AccessUser))):
    # Postal code validation
    try:
        float(postal_code)
    except ValueError:
        return JSONResponse(status_code=400, content="Invalid postal code")

    # Get postal codes in the same postal sector (https://en.wikipedia.org/wiki/Postal_codes_in_Singapore)
    postal_group = postalcodes.get_postals_in_group(postal_code)

    # Shortlist potential sessions to reduce onemap api calls
    potential_sessions = []
    for postal in postal_group:
        potential_sessions += session.get_sessions_by_postal_prefix(postal)

    # TODO filter by timing

    # Fine grained filtering to limit walking distance between source and origin to 500m
    origin = api.get_lat_long(postal_code)
    suitable_sessions = []
    for potential_session in potential_sessions:
        dest = api.get_lat_long(potential_session["postal_code"])
        distance = api.calculate_distance(origin, dest)
        if distance <= 500:
            suitable_sessions.append(potential_session)

    return suitable_sessions


# Join session
@app.post("/session/join", tags=["session"], description="Join session.")
def join_session(session_code_dto: SessionCodeDTO, AccessUser=Depends(auth.claim(AccessUser))):
    # Retrieve existing session
    existing_session = session.get_session(session_code_dto.session_code)

    if not existing_session:
        return JSONResponse(status_code=400, content="Invalid session code.")

    # Add session to user object & update user object
    user_object = user.get_user(session_code_dto.username)

    if not user_object:
        return JSONResponse(status_code=400, content="Invalid username.")

    updated_sessions = user_object["active_sessions"]
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
    rating = rate_user_dto.rating
    if (rating < 0 or rating > 5):
        return JSONResponse(status_code=400, content="Invalid rating given.")
    # Retrieve user to be rated
    user_to_rate_object = user.get_user(rate_user_dto.dabaoer)

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
    user_object = user.get_user(rate_user_dto.username)
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
@app.get("/user/account/{username}", tags=["user"], description="Retrieve user profile.")
def list_user_sessions(username, AccessUser=Depends(auth.claim(AccessUser))):
    # TODO return Auth0 user details here as well
    user_object = user.get_user(username)
    return user_object


# TODO leaderboard logic


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
