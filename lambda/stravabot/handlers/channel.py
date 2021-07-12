from typing import Callable

from stravabot.services.slack import SlackService, SlackServiceError


class ChannelHandler:
    def __init__(self, slack: SlackService):
        self.slack = slack

    def handle_kick_command(self, ack: Callable, body: dict) -> None:
        channel_id = body["channel_id"]
        try:
            self.slack.leave_channel(channel_id)
            ack()
        except SlackServiceError as e:
            ack(str(e))
