from dotenv import load_dotenv
import os
load_dotenv()

DETA_BASE_PROJECT_KEY = os.environ["DETA_BASE_PROJECT_KEY"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_API_AUDIENCE = os.environ["AUTH0_API_AUDIENCE"]
MGMT_AUTH_CLIENT_ID = os.environ["MGMT_AUTH_CLIENT_ID"]
MGMT_AUTH_CLIENT_SECRET = os.environ["MGMT_AUTH_CLIENT_SECRET"]
AUTH_URL = os.environ["AUTH_URL"]
