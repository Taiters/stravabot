from .blocks import *  # noqa
from .elements import *  # noqa


def response(*blocks: dict, response_type: str = "ephemeral", replace_original: bool = False) -> dict:
    return {
        "response_type": response_type,
        "replace_original": replace_original,
        "blocks": blocks,
    }


def message(*blocks: dict) -> dict:
    return {
        "blocks": blocks,
    }


def field(title: str, value: str) -> dict:
    return mrkdwn(f"*{title}*\n{value}")  # noqa
