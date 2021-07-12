from slack_bolt import App


class SlackServiceError(Exception):
    pass


class SlackService:
    def __init__(self, slack: App):
        self.slack = slack

    def post_to_channels(self, *blocks: dict) -> None:
        all_channels = self.slack.client.conversations_list()
        if not all_channels["ok"]:
            raise SlackServiceError(f"Error getting channel list: {all_channels['error']}")

        in_channels = (c for c in all_channels["channels"] if c.get("is_channel", False) and c.get("is_member", False))
        channel_ids = [c["id"] for c in in_channels]

        for channel_id in channel_ids:
            self.slack.client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
            )
