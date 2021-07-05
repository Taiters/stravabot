from typing import Optional


def context(*elements: dict) -> dict:
    return {"type": "context", "elements": elements}


def section(text: dict, accessory: Optional[dict] = None) -> dict:
    section = {
        "type": "section",
        "text": text,
    }
    if accessory:
        section["accessory"] = accessory
    return section


def actions(*elements: dict) -> dict:
    return {"type": "actions", "elements": elements}


def mrkdwn(text: str) -> dict:
    return {
        "type": "mrkdwn",
        "text": text,
    }


def button(text: str, value: str, action_id: str, url: Optional[str] = None, style: str = "default") -> dict:
    button = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True,
        },
        "style": style,
        "value": value,
        "action_id": action_id,
    }
    if url:
        button["url"] = url
    return button


def help(command: str, sub_commands: list) -> dict:
    return {
        "response_type": "ephemeral",
        "blocks": [
            context(mrkdwn("Available commands")),
            context(mrkdwn("\n".join(f"`{command} {c.text}`\n\t\t{c.help}" for c in sub_commands))),
        ],
    }


def unknown_sub_command(command: str, sub_command: str) -> dict:
    return {
        "response_type": "ephemeral",
        "blocks": [
            context(mrkdwn(f"Unknown command: `{sub_command}`\nUse `{command} help` to view available commands"))
        ],
    }


def connect_response(action_id: str, token: str, oauth_url: str) -> dict:
    return {
        "response_type": "ephemeral",
        "blocks": [
            actions(
                button(
                    text="Connect to Strava",
                    action_id=action_id,
                    value=token,
                    url=oauth_url,
                    style="primary",
                ),
            ),
        ],
    }


def connect_result(success: bool = True) -> dict:
    return {
        "response_type": "ephemeral",
        "replace_original": True,
        "blocks": [
            context(mrkdwn("Done :thumbsup:" if success else "Denied :thumbsdown:")),
        ],
    }


def disconnect_response(error: Optional[str] = None) -> dict:
    return {
        "response_type": "ephemeral",
        "blocks": [context(mrkdwn(error if error else "So long :wave:"))],
    }
