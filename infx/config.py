from infx.utils import ssm_param

DOMAIN = "stravabot.dotslashdan.com"

KV_KEY_RECORD = "record_key"
KV_TTL_RECORD = "record_expiry"

BASE_ENVIRONMENT = {
    "SLACK_BOT_TOKEN": ssm_param("slack_bot_token", 2),
    "SLACK_SIGNING_SECRET": ssm_param("slack_signing_secret", 3),
    "STRAVA_CLIENT_ID": ssm_param("strava_client_id"),
    "STRAVA_CLIENT_SECRET": ssm_param("strava_client_secret"),
    "STRAVA_WEBHOOK_VERIFY_TOKEN": ssm_param("strava_webhook_verify_token"),
    "JWT_SECRET_KEY": ssm_param("jwt_secret_key"),
    "MAPBOX_ACCESS_TOKEN": ssm_param("mapbox_access_token"),
    "STRAVABOT_ENV": "prod",
}
