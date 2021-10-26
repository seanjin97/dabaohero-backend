from deta import Deta
import config

deta = Deta(config.DETA_BASE_PROJECT_KEY)

sessionDB = deta.Base("sessions")


def create_session(session):
    new_session = sessionDB.insert(session)
    return new_session


def get_session(key):
    session_object = sessionDB.get(key)
    return session_object


def update_session(updated_session):
    return sessionDB.put(updated_session)


def delete_session(key):
    sessionDB.delete(key)


# Retrieve only active sessions with prefixed postal code value
def get_sessions_by_postal_prefix_and_time(prefix, time, leecher):
    query = {"postal_code?pfx":  prefix,
             "is_active": True,
             "departure_time?gt": time,
             "leechers?not_contains": leecher}
    sessions = sessionDB.fetch(query)

    return sessions
