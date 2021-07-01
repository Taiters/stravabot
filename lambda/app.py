from uuid import uuid4
from datetime import timedelta

import requests
from jose.exceptions import JWTError
from aws_xray_sdk.core import patch_all


from stravabot import auth, strava, messages
from stravabot.api import Api, ApiRequest, ApiResponse
from stravabot.db import KeyValueStore


patch_all()
api = Api()
kv_store = KeyValueStore()


with api.command("/creep") as creep:

    @creep.on("connect", "Connect to your Strava account")
    def connect(body, ack):
        token = auth.generate_token(
            user_id=body["user_id"],
            claims={"response_id": str(uuid4())},
            ttl=timedelta(minutes=10),
        )
        oauth_url = strava.get_oauth_url(token)
        response = messages.connect_response("authenticate_clicked", token, oauth_url)
        ack(response)


@api.slack.action("authenticate_clicked")  # type: ignore
def authenticate_clicked(ack, action, body):
    response_url = body["response_url"]
    token = auth.decode_token(action["value"])
    user_id = token["sub"]
    response_id = token["response_id"]
    expires = token["exp"]
    kv_store.put(
        f"response_id:{user_id}:{response_id}",
        {"response_url": response_url},
        expires=expires,
    )
    ack()


@api.route("/strava/auth", methods=["GET"])
def strava_auth(request: ApiRequest) -> ApiResponse:
    if "token" not in request.query_parameters:
        return ApiResponse.bad_request()

    token = request.query_parameters["token"]
    try:
        decoded_token = auth.decode_token(token)
    except JWTError:
        return ApiResponse.bad_request()

    user_id = decoded_token["sub"]
    response_id = decoded_token["response_id"]
    result = kv_store.get(f"response_id:{user_id}:{response_id}")

    if not result or "response_url" not in result:
        return ApiResponse.bad_request()

    if "error" in request.query_parameters:
        requests.post(result["response_url"], json=messages.connect_result(success=False))
        return ApiResponse(body="Denied")

    code = request.query_parameters["code"]
    token = strava.exchange_token(code)
    athlete = token["athlete"]
    kv_store.put(
        key=f"user:{athlete['id']}",
        value={
            "access_token": token["access_token"],
            "token_expires_at": token["expires_at"],
            "refresh_token": token["refresh_token"],
            "strava_id": athlete["id"],
            "slack_id": user_id,
        },
    )

    requests.post(result["response_url"], json=messages.connect_result())
    return ApiResponse(body="Gravy")


def handler(event, context):
    return api.handle(event, context)
