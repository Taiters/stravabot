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


def mrkdwn(text: str) -> dict:
    return {
        "type": "mrkdwn",
        "text": text,
    }


def button(text: str, value: str, action_id: str, url: Optional[str] = None) -> dict:
    button = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True,
        },
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
            section(
                text=mrkdwn("Smashing, let's get started :point_right:"),
                accessory=button(
                    text="Authenticate",
                    action_id=action_id,
                    value=token,
                    url=oauth_url,
                ),
            )
        ],
    }


def connect_result(success: bool = True) -> dict:
    return {
        "response_type": "ephemeral",
        "replace_original": True,
        "blocks": [
            section(
                text=mrkdwn("Done :thumbsup:" if success else "Denied :thumbsdown:"),
            )
        ],
    }
