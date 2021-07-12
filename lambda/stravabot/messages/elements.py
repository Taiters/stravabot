def plain_text(text: str, emoji: bool = True) -> dict:
    return {
        "type": "plain_text",
        "text": text,
        "emoji": emoji,
    }


def mrkdwn(mrkdwn: str, emoji: bool = True) -> dict:
    return {
        "type": "mrkdwn",
        "text": mrkdwn,
    }


def button(text: dict, action_id: str, url: str, value: str, style: str = "default") -> dict:
    return {
        "type": "button",
        "text": text,
        "action_id": action_id,
        "url": url,
        "value": value,
        "style": style,
    }
