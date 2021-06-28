from stravabot import strava
from stravabot.api import Api


api = Api()


with api.command("/creep") as creep:

    @creep.on("connect", "Connect to your Strava account")
    def connect(ack, say):
        ack(strava.get_oauth_url("user", "token"))


def handler(event, context):
    return api.handle(event, context)
