from typing import Any, Dict, Optional


def section(*fields: dict, accessory: Optional[dict] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "type": "section",
    }
    if len(fields) > 1:
        result["fields"] = fields
    else:
        result["text"] = fields[0]
    if accessory:
        result["accessory"] = accessory
    return result


def context(*elements: dict) -> dict:
    return {"type": "context", "elements": elements}


def image(image_url: str, alt_text: str, title: dict) -> dict:
    return {
        "type": "image",
        "image_url": image_url,
        "alt_text": alt_text,
        "title": title,
    }


def actions(*elements: dict) -> dict:
    return {
        "type": "actions",
        "elements": elements,
    }
