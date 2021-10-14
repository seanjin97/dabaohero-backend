from deta import Deta
from dabaohero_backend import config

deta = Deta(config.DETA_BASE_PROJECT_KEY)

userDB = deta.Base("users")


# Create user
def create_user(user_object):
    new_user = userDB.insert(user_object)
    return new_user


# Get user by username
def get_user(key):
    user_object = userDB.get(key)
    return user_object


# Update user object with new ouser object
def update_user(updated_user):
    return userDB.put(updated_user)
