import os

KV_STORE_TABLE = os.environ["KV_STORE_TABLE"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

STRAVA_CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
STRAVA_CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

STRAVA_CALLBACK_URL = "https://stravabot.dotslashdan.com/strava/auth"
