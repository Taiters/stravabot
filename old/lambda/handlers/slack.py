from dataclasses import dataclass
from typing import Callable

import boto3
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE
from stravabot.config.base import AUTH_FLOW_TTL
from stravabot.db import KeyValueStore
from stravabot.messages import actions, button, context, mrkdwn, plain_text, response
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.slack import NotInChannelError, SlackService, SlackServiceError
from stravabot.services.strava import StravaService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService

COMMAND_NAME = "/creep"


@dataclass
class Command:
    name: str
    cmd: Callable
    help: str


app = App(process_before_response=True)
slack_handler = SlackRequestHandler(app)

dynamodb = boto3.resource("dynamodb")
store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))

tokens = TokenService(JWT_SECRET_KEY)
users = UserService(store)
strava = StravaService(users)
response_urls = ResponseUrlService(store, tokens)
slack = SlackService(app)


def connect(ack: Callable, body: dict) -> None:
    token = response_urls.generate_token(body["user_id"], AUTH_FLOW_TTL)
    oauth_url = strava.get_oauth_url(token.token)
    ack(
        response(
            actions(
                button(
                    text=plain_text("Connect to Strava"),
                    action_id="authenticate_clicked",
                    value=token.token,
                    url=oauth_url,
                    style="primary",
                )
            )
        )
    )


def disconnect(ack: Callable, body: dict) -> None:
    user_id = body["user_id"]
    user = users.get_by_slack_id(user_id)
    if user is None:
        ack(
            response(
                context(
                    mrkdwn(
                        "What is this!? I can't find you. You can't disconnect without connecting. Maybe you should connect instead..."
                    )
                )
            )
        )
    else:
        with strava.session(user) as session:
            session.deauthorize()
        ack(response(context(mrkdwn("So long :wave:"))))


def kick(ack: Callable, body: dict) -> None:
    channel_id = body["channel_id"]
    try:
        slack.leave_channel(channel_id)
        ack(response(context(mrkdwn("I know when I'm not wanted, farewell"))))
    except NotInChannelError:
        ack(response(context(mrkdwn("I'm not _in_ the channel.. Still waiting for the invite :wink:"))))
    except SlackServiceError as e:
        ack(str(e))


def authenticate_clicked(ack: Callable, body: dict, action: dict) -> None:
    token = tokens.decode(action["value"])
    response_url = body["response_url"]
    response_urls.put(token, response_url)
    ack()


def _match_name(cmd: Command) -> Callable[[dict], bool]:
    def match(command: dict) -> bool:
        if "text" not in command:
            return False
        return command["text"].strip().lower().startswith(cmd.name)

    return match


commands = [
    Command("connect", connect, "Connect to your Strava account"),
    Command("disconnect", disconnect, "Disconnect your Strava account"),
    Command("kick", kick, "Remove from the current channel"),
]

app.action("authenticate_clicked")(authenticate_clicked)  # type: ignore
for c in commands:
    app.command(COMMAND_NAME, matchers=[_match_name(c)])(c.cmd)  # type: ignore


@app.command(COMMAND_NAME)  # type: ignore
def help(ack: Callable) -> None:
    ack(
        response(
            context(mrkdwn("Available commands")),
            context(mrkdwn("\n".join(f"`{COMMAND_NAME} {c.name}`\n\t\t{c.help}" for c in commands))),
        )
    )


def handler(event: dict, context: dict) -> dict:
    return slack_handler.handle(event, context)
