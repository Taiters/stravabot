from typing import Any

import requests

from stravabot.config import MAPBOX_ACCESS_TOKEN


def static_image(overlay: str, width: int = 500, height: int = 300) -> Any:
    url = f"https://api.mapbox.com/styles/v1/mapbox/light-v10/static/{overlay}/auto/{width}x{height}?access_token={MAPBOX_ACCESS_TOKEN}"
    return requests.get(url, stream=True).raw
