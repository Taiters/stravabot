import requests

from stravabot.config import WEATHER_API_KEY
from stravabot.models import Location

BASE_URL = "https://api.weatherapi.com/v1"


def current(location: Location) -> dict:
    response = requests.get(
        f"{BASE_URL}/current.json", params={"key": WEATHER_API_KEY, "q": f"{location.latitude},{location.longitude}"}
    )
    return response.json()
