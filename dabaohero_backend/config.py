from dotenv import load_dotenv
import os
load_dotenv()

DETA_BASE_PROJECT_KEY = os.environ["DETA_BASE_PROJECT_KEY"]
AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_API_AUDIENCE = os.environ["AUTH0_API_AUDIENCE"]
