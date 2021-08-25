from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class UserAccessToken:
    token: str
    expires_at: int
    refresh_token: str


@dataclass
class User:
    strava_id: int
    slack_id: str
    strava_access_token: UserAccessToken

    @staticmethod
    def from_dict(data: dict) -> User:
        token = data["strava_access_token"]
        return User(
            strava_id=int(data["strava_id"]),
            slack_id=data["slack_id"],
            strava_access_token=UserAccessToken(
                token=token["token"],
                expires_at=int(token["expires_at"]),
                refresh_token=token["refresh_token"],
            ),
        )


@dataclass
class Token:
    slack_user_id: str
    data: dict
    token: str
    expires: Optional[int] = None


@dataclass
class Location:
    latitude: float
    longitude: float


class StravaAspectType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class StravaObjectType(Enum):
    ATHLETE = "athlete"
    ACTIVITY = "activity"


@dataclass
class StravaEvent:
    owner_id: int
    object_id: int
    subscription_id: int
    aspect_type: StravaAspectType
    object_type: StravaObjectType
    event_time: datetime
    updates: dict
    dry_run: bool

    @staticmethod
    def from_dict(data: dict) -> StravaEvent:
        return StravaEvent(
            owner_id=int(data["owner_id"]),
            object_id=int(data["object_id"]),
            subscription_id=int(data["subscription_id"]),
            aspect_type=StravaAspectType(data["aspect_type"]),
            object_type=StravaObjectType(data["object_type"]),
            event_time=datetime.fromtimestamp(data["event_time"]),
            updates=data.get("updates", {}),
            dry_run=data.get("dry_run", False),
        )


class StravaActivityType(Enum):
    AlpineSki = "AlpineSki"
    BackcountrySki = "BackcountrySki"
    Canoeing = "Canoeing"
    Crossfit = "Crossfit"
    EBikeRide = "EBikeRide"
    Elliptical = "Elliptical"
    Golf = "Golf"
    Handcycle = "Handcycle"
    Hike = "Hike"
    IceSkate = "IceSkate"
    InlineSkate = "InlineSkate"
    Kayaking = "Kayaking"
    Kitesurf = "Kitesurf"
    NordicSki = "NordicSki"
    Ride = "Ride"
    RockClimbing = "RockClimbing"
    RollerSki = "RollerSki"
    Rowing = "Rowing"
    Run = "Run"
    Sail = "Sail"
    Skateboard = "Skateboard"
    Snowboard = "Snowboard"
    Snowshoe = "Snowshoe"
    Soccer = "Soccer"
    StairStepper = "StairStepper"
    StandUpPaddling = "StandUpPaddling"
    Surfing = "Surfing"
    Swim = "Swim"
    Velomobile = "Velomobile"
    VirtualRide = "VirtualRide"
    VirtualRun = "VirtualRun"
    Walk = "Walk"
    WeightTraining = "WeightTraining"
    Wheelchair = "Wheelchair"
    Windsurf = "Windsurf"
    Workout = "Workout"
    Yoga = "Yoga"


@dataclass
class StravaActivity:
    activity_id: int
    name: str
    description: str
    distance: int
    moving_time: int
    elapsed_time: int
    average_speed: int
    polyline: str
    activity_type: StravaActivityType
    start_location: Location

    @staticmethod
    def from_dict(data: dict) -> StravaActivity:
        return StravaActivity(
            activity_id=int(data["id"]),
            name=data["name"],
            description=data["description"],
            distance=int(data["distance"]),
            moving_time=int(data["moving_time"]),
            elapsed_time=int(data["elapsed_time"]),
            average_speed=int(data["average_speed"]),
            polyline=data["map"]["summary_polyline"],
            activity_type=StravaActivityType(data["type"]),
            start_location=Location(
                latitude=float(data["start_latlng"][0]),
                longitude=float(data["start_latlng"][1]),
            ),
        )

    @property
    def seconds_per_km(self) -> int:
        return int(1000 / (self.distance / self.moving_time))
