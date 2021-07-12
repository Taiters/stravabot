from stravabot.messages import field, image, plain_text, section
from stravabot.models import StravaAspectType, StravaEvent, StravaObjectType
from stravabot.services.map import MapService
from stravabot.services.slack import SlackService
from stravabot.services.strava import StravaService
from stravabot.services.user import UserService
from stravabot.utils import seconds_to_minutes


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

        self.slack.post_to_channels(
            section(plain_text(f"<@{user.slack_id}> has completed a run")),
            section(
                field("Distance", f"{round(activity.distance / 1000, 2)}km"),
                field("Pace", f"{seconds_to_minutes(activity.seconds_per_km)}/km"),
                field("Elapsed Time", seconds_to_minutes(activity.elapsed_time)),
                field("Moving Time", seconds_to_minutes(activity.moving_time)),
            ),
            image(
                image_url=self.maps.generate_map(activity),
                title=plain_text(activity.name),
                alt_text=activity.name,
            ),
        )
