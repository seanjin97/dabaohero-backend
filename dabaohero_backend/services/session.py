from dao import sessions
import uuid


# Create a new session and updates user object
def create_session(session_dto):
    # Retrieve request body
    username = session_dto.username
    session_code = str(uuid.uuid4())

    epoch_time = int(session_dto.departure_time.timestamp())

    # Create new session
    new_session = {
        "key": session_code,
        "postal_code": session_dto.postal_code,
        "food": session_dto.food,
        "departure_time": epoch_time,
        "dabaoer": username,
        "leechers": [],
        "is_active": True
    }
    # Create session
    try:
        created_session = sessions.create_session(new_session)
        return created_session
    except Exception as e:
        print("services.session.create_session:", e)


# Delete session by session_code
def delete_session(session_code):
    try:
        sessions.delete_session(session_code)
    except Exception as e:
        print("services.session.delete_session:", e)


# Get session by session_code
def get_session(session_code):
    try:
        session_object = sessions.get_session(session_code)
        return session_object
    except Exception as e:
        print("services.session.session_code:", e)


# Get sessions by host
def get_sessions_by_dabaoer(username):
    retrieved_sessions = sessions.get_sessions_by_dabaoer(username)
    return retrieved_sessions.items


# Get sessions by postal code group
def get_sessions_by_postal_prefix_and_time(prefix, time):
    retrieved_sessions = sessions.get_sessions_by_postal_prefix_and_time(
        prefix, time)

    return retrieved_sessions.items


# Update session with new session object
def update_session(session_object):
    try:
        updated_session_object = sessions.update_session(session_object)
        return updated_session_object
    except Exception as e:
        print("services.session.update_session:", e)
