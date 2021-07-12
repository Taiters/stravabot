from hashlib import sha224
from urllib.parse import quote_plus

import polyline
from boto3_type_annotations.s3 import Bucket
from botocore.exceptions import ClientError

from stravabot.clients import mapbox
from stravabot.config import CDN_HOST
from stravabot.models import StravaActivity


def _marker(location: list, size: str = "l", label: str = "a", color: str = "2CB5F2") -> str:
    return f"pin-{size}-{label}+{color}({location[1]},{location[0]})"


def _path(polyline: str, width: int = 3, stroke_color: str = "2CB5F2", stroke_opacity: int = 1) -> str:
    return f"path-{width}+{stroke_color}-{stroke_opacity}({quote_plus(polyline)})"


class MapService:
    def __init__(self, bucket: Bucket):
        self.bucket = bucket

    def _exists(self, key):
        try:
            self.bucket.Object(key).load()
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
        return True

    def generate_map(self, activity: StravaActivity) -> str:
        route = polyline.decode(activity.polyline)
        overlay = f"{_marker(route[0], label='s')},{_marker(route[-1], label='e')},{_path(activity.polyline)}"
        key = f"routes/{sha224(overlay.encode('utf-8')).hexdigest()}.png"

        if not self._exists(key):
            image = mapbox.static_image(overlay)
            self.bucket.upload_fileobj(image, key, ExtraArgs={"ContentType": "image/png"})

        return f"{CDN_HOST}/{key}"
