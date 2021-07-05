from stravabot.api import ApiRequest, ApiResponse
from stravabot.config import STRAVA_WEBHOOK_VERIFY_TOKEN
from stravabot.services.event import EventService


class StravaEventHandler:
    def __init__(self, events: EventService):
        self.events = events

    def handle_verify(self, request: ApiRequest) -> ApiResponse:
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

    def handle_webhook(self, request: ApiRequest) -> ApiResponse:
        self.events.send_event(request.body)
        return ApiResponse.ok()
