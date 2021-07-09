import json
from dataclasses import asdict
from typing import Callable

from stravabot.messages import mrkdwn, response, section
from stravabot.services.user import UserService


class DebugHandler:
    def __init__(self, users: UserService):
        self.users = users

    def handle_debug(self, ack: Callable, body: dict) -> None:
        user_id = body["user_id"]
        user = self.users.get_by_slack_id(user_id)
        if user is None:
            ack("You are not connected")
        else:
            user_dict = asdict(user)
            user_dict["strava_access_token"]["refresh_token"] = "***"
            ack(response(section(mrkdwn(f"```{json.dumps(user_dict, indent=4)}```"))))
