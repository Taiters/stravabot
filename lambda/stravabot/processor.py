from stravabot.models import StravaEvent
from stravabot.services.user import UserService


class StravaEventProcessor:
    def __init__(self, users: UserService):
        self.users = users

    def process(self, event: StravaEvent) -> None:
        print(event)
        if event.updates.get("authorized") == "false":
            self.users.delete(str(event.owner_id))
