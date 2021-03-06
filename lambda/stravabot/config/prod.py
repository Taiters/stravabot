import os

KV_STORE_TABLE = os.environ["KV_STORE_TABLE"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
CDN_BUCKET = os.environ.get("CDN_BUCKET", "")

STRAVA_CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
STRAVA_CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
STRAVA_WEBHOOK_VERIFY_TOKEN = os.environ["STRAVA_WEBHOOK_VERIFY_TOKEN"]
STRAVA_EVENT_HANDLER = os.environ.get("STRAVA_EVENT_HANDLER", "")
STRAVA_CALLBACK_URL = "https://stravabot.dotslashdan.com/strava/auth"

MAPBOX_ACCESS_TOKEN = os.environ["MAPBOX_ACCESS_TOKEN"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
