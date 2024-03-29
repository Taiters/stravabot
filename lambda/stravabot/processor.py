import json

from stravabot.clients import weather  # Should wrap this up
from stravabot.messages import context, field, image, mrkdwn, plain_text, section
from stravabot.models import (
    StravaActivityType,
    StravaAspectType,
    StravaEvent,
    StravaObjectType,
)
from stravabot.services.map import MapService
from stravabot.services.slack import SlackService
from stravabot.services.strava import StravaService
from stravabot.services.user import UserService
from stravabot.utils import format_time


class StravaEventProcessor:
    def __init__(self, users: UserService, strava: StravaService, maps: MapService, slack: SlackService):
        self.users = users
        self.strava = strava
        self.maps = maps
        self.slack = slack

    def process(self, event: StravaEvent) -> None:
        if event.updates.get("authorized") == "false":
            self.users.delete(event.owner_id)
            return

        if event.aspect_type is not StravaAspectType.CREATE or event.object_type is not StravaObjectType.ACTIVITY:
            return

        user = self.users.get_by_strava_id(event.owner_id)
        if user is None:
            return

        with self.strava.session(user) as session:
            activity = session.activity(event.object_id)

        if activity.activity_type not in {StravaActivityType.Run, StravaActivityType.Walk}:
            return

        weather_data = weather.current(activity.start_location)
        weather_condition = weather_data["current"]["condition"]["text"]
        weather_temp = int(weather_data["current"]["temp_c"])
        message = f"<@{user.slack_id}> did the {activity.activity_type.value.lower()}!"
        blocks = [
            section(mrkdwn(message)),
            section(
                field("Distance", f"{round(activity.distance / 1000, 2)}km"),
                field("Pace", f"{format_time(activity.seconds_per_km)}/km"),
                field("Elapsed Time", format_time(activity.elapsed_time)),
                field("Weather", f"{weather_condition} ({weather_temp}℃)"),
            ),
            image(
                image_url=self.maps.generate_map(activity),
                title=plain_text(activity.name),
                alt_text=activity.name,
            ),
            context(mrkdwn(f"<{self.strava.get_activity_url(activity)}|Open in Strava> :point_left: give some kudos!")),
        ]

        if event.dry_run:
            print(f"Dry run event: {message}\nBlocks: {json.dumps(blocks, indent=4)}")
        else:
            self.slack.post_to_channels(
                text=message,
                blocks=blocks,
            )
