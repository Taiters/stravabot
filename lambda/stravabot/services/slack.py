from slack_bolt import App
from slack_sdk.errors import SlackApiError


class SlackServiceError(Exception):
    pass


class SlackService:
    def __init__(self, slack: App):
        self.slack = slack

    def post_to_channels(self, text: str, blocks: list) -> None:
        all_channels = self.slack.client.conversations_list(types="public_channel,private_channel")
        if not all_channels["ok"]:
            raise SlackServiceError(f"Error getting channel list: {all_channels['error']}")

        in_channels = (c for c in all_channels["channels"] if c.get("is_channel", False) and c.get("is_member", False))
        channel_ids = [c["id"] for c in in_channels]

        for channel_id in channel_ids:
            self.slack.client.chat_postMessage(
                channel=channel_id,
                text=text,
                blocks=blocks,
            )

    def leave_channel(self, channel_id: str) -> None:
        try:
            result = self.slack.client.conversations_leave(channel=channel_id)
        except SlackApiError as e:
            raise SlackServiceError(e)

        if not result["ok"]:
            raise SlackServiceError(result["error"])
