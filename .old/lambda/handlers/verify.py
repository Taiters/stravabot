import os

from stravabot.api import ApiRequest, api_endpoint, bad_request

STRAVA_VERIFY_TOKEN = os.environ["STRAVA_WEBHOOK_VERIFY_TOKEN"]


@api_endpoint
def handler(request: ApiRequest) -> dict:
    if (
        "hub.verify_token" not in request.query_parameters
        or "hub.challenge" not in request.query_parameters
        or "hub.mode" not in request.query_parameters
    ):
        return bad_request()

    verify_token = request.query_parameters["hub.verify_token"]
    challenge = request.query_parameters["hub.challenge"]
    mode = request.query_parameters["hub.mode"]

    if verify_token != STRAVA_VERIFY_TOKEN or mode != "subscribe":
        return bad_request()

    return {"hub.challenge": challenge}
