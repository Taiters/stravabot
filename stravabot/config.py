from aws_cdk.aws_apigatewayv2 import HttpMethod

from stravabot.utils import ssm_param


DOMAIN = "stravabot.dotslashdan.com"

ROUTES = [
    ([HttpMethod.GET], "/strava/auth"),
]

KV_KEY_RECORD = "record_key"
KV_TTL_RECORD = "record_expiry"

SLACK_BOT_TOKEN = ssm_param("slack_bot_token", 2)
SLACK_SIGNING_SECRET = ssm_param("slack_signing_secret", 3)
STRAVA_CLIENT_ID = ssm_param("strava_client_id")
STRAVA_CLIENT_SECRET = ssm_param("strava_client_secret")
JWT_SECRET_KEY = ssm_param("jwt_secret_key")
