from deta import Deta
import config

deta = Deta(config.DETA_BASE_PROJECT_KEY)

userDB = deta.Base("users")


def create_user(username,):
    user_object = {"key": username, "completed_orders": 0,
                   "orders_requested": 0, "rating": 0, "active_sessions": []}
    new_user = userDB.insert(user_object)
    return new_user
