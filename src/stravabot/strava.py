from urllib.parse import urlencode

from stravabot.config import STRAVA_CLIENT_ID


CALLBACK_URL = f"https://localhost:3000/strava/auth"


def get_oauth_url(user_id, token):
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": f"{CALLBACK_URL}?token={user_id}:{token}",
        "response_type": "code",
        "scope": "read,activity:read",
    }
    return f"https://www.strava.com/oauth/authorize?{urlencode(params)}"
