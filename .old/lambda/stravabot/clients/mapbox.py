from typing import Any

import requests

from stravabot.config import MAPBOX_ACCESS_TOKEN

BASE_URL = "https://api.mapbox.com"


class MapboxError(Exception):
    pass


def static_image(overlay: str, width: int = 500, height: int = 300) -> Any:
    url = f"{BASE_URL}/styles/v1/mapbox/light-v10/static/{overlay}/auto/{width}x{height}?access_token={MAPBOX_ACCESS_TOKEN}"
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        raise MapboxError(f"Unexpected status code: {response.status_code}")

    return response.raw
