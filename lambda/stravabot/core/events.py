from stravabot.api import ApiRequest, ApiResponse
from stravabot.config import STRAVA_WEBHOOK_VERIFY_TOKEN
from stravabot.models import StravaEvent
from stravabot.services.user import UserService


def verify(request: ApiRequest) -> ApiResponse:
    if (
        "hub.verify_token" not in request.query_parameters
        or "hub.challenge" not in request.query_parameters
        or "hub.mode" not in request.query_parameters
    ):
        return ApiResponse.bad_request()

    verify_token = request.query_parameters["hub.verify_token"]
    challenge = request.query_parameters["hub.challenge"]
    mode = request.query_parameters["hub.mode"]

    if verify_token != STRAVA_WEBHOOK_VERIFY_TOKEN or mode != "subscribe":
        return ApiResponse.bad_request()

    return ApiResponse(body={"hub.challenge": challenge})


class StravaEventHandler:
    def __init__(self, users: UserService):
        self.users = users

    def handle(self, event: StravaEvent) -> None:
        print(event)
        if event.updates.get("authorized") == "false":
            self.users.delete(str(event.owner_id))
