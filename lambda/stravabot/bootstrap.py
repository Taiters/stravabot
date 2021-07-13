import logging
from contextlib import contextmanager
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@contextmanager
def timed(name):
    start = time.time()
    yield
    end = time.time()
    logging.info(f"importing {name} took {end - start} seconds")


with timed("boto3"):
    import boto3

with timed("jinja2"):
    from jinja2 import Environment, PackageLoader, select_autoescape

with timed("slack_bolt"):
    from slack_bolt import App

with timed("stravabot.api"):
    from stravabot.api import Api

with timed("stravabot.config"):
    from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE, STRAVA_EVENT_HANDLER, AUTH_FLOW_TTL

with timed("stravabot.db"):
    from stravabot.db import KeyValueStore

with timed("stravabot.handlers"):
    from stravabot.handlers import StravaAuthHandler, StravaEventHandler

with timed("stravabot.handlers.channel"):
    from stravabot.handlers.channel import ChannelHandler

with timed("stravabot.services.event"):
    from stravabot.services.event import EventService

with timed("stravabot.services.response_url"):
    from stravabot.services.response_url import ResponseUrlService

with timed("stravabot.services.slack"):
    from stravabot.services.slack import SlackService

with timed("stravabot.services.strava"):
    from stravabot.services.strava import StravaService

with timed("stravabot.services.token"):
    from stravabot.services.token import TokenService

with timed("stravabot.services.user"):
    from stravabot.services.user import UserService

def bootstrap() -> Api:
    logger.info("bootstrap starting")
    # templates = Environment(
    #     loader=PackageLoader("stravabot"),
    #     autoescape=select_autoescape(),
    # )
    # app = App(process_before_response=True)
    api = Api(None)
    # dynamodb = boto3.resource("dynamodb")
    # store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))

    # tokens = TokenService(JWT_SECRET_KEY)
    # users = UserService(store)
    # strava = StravaService(users)
    # response_urls = ResponseUrlService(store, tokens)
    events = EventService(STRAVA_EVENT_HANDLER, boto3.client("lambda"))
    # slack = SlackService(app)

    # channel_handler = ChannelHandler(slack)
    # auth_handler = StravaAuthHandler(templates, users, strava, tokens, response_urls, AUTH_FLOW_TTL)
    # with api.command("/creep") as creep:
    #     creep.on("connect", "Connect to your Strava account")(auth_handler.handle_connect_command)
    #     creep.on("disconnect", "Disconnect your Strava account")(auth_handler.handle_disconnect_command)
    #     creep.on("kick", "Remove from the current channel")(channel_handler.handle_kick_command)

    # api.slack.action("authenticate_clicked")(auth_handler.handle_authenticate_action)  # type: ignore
    # api.route("/strava/auth", methods=["GET"])(auth_handler.handle_strava_callback)
    # api.route("/strava/auth", methods=["POST"])(auth_handler.handle_strava_connect)

    event_handler = StravaEventHandler(events)
    api.route("/strava/event", methods=["POST"])(event_handler.handle_webhook)
    # api.route("/strava/event", methods=["GET"])(event_handler.handle_verify)

    logger.info("bootstrap ending")
    return api
