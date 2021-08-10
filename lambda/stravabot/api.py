import functools
import json
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ApiRequest:
    path: str
    method: str
    path_parameters: dict = field(default_factory=dict)
    query_parameters: dict = field(default_factory=dict)
    body: str = ""

    def json(self) -> dict:
        return json.loads(self.body)


def api_endpoint(func: Callable[[ApiRequest], Optional[dict]]) -> Callable[[dict, dict], Optional[dict]]:
    @functools.wraps(func)
    def wrapper(event: dict, context: dict) -> Optional[dict]:
        http = event["requestContext"]["http"]
        return func(
            ApiRequest(
                path=http["path"],
                method=http["method"],
                path_parameters=event.get("pathParameters", {}),
                query_parameters=event.get("queryStringParameters", {}),
                body=event.get("body", ""),
            )
        )

    return wrapper


def bad_request(body: Optional[dict] = None) -> dict:
    return {"statusCode": 400, "body": body}
