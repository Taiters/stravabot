from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union

from slack_bolt.app.app import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from stravabot.messages import help, unknown_sub_command


def _default_headers() -> dict:
    return {"Content-Type": "application/json"}


@dataclass
class ApiRequest:
    path: str
    method: str
    path_parameters: dict
    query_parameters: dict


@dataclass
class ApiResponse:
    body: Optional[Union[str, dict]] = None
    status: int = 200
    headers: dict = field(default_factory=_default_headers)

    @staticmethod
    def bad_request():
        return ApiResponse(status=400)


def map_api_request(event: dict) -> ApiRequest:
    http = event["requestContext"]["http"]
    return ApiRequest(
        path=http["path"],
        method=http["method"],
        path_parameters=event.get("pathParameters", {}),
        query_parameters=event.get("queryStringParameters", {}),
    )


def map_api_response(response: ApiResponse) -> dict:
    return {
        "statusCode": response.status,
        "body": response.body,
        "headers": response.headers,
    }


@dataclass
class SubCommand:
    text: str
    func: Callable
    help: Optional[str] = None


def _match_sub_command(sub_command: SubCommand) -> Callable[[dict], bool]:
    def match(command: dict) -> bool:
        if "text" not in command:
            return False
        return command["text"].strip().lower() == sub_command.text

    return match


class CommandBuilder:
    def __init__(self, command: str, slack_app: App, base_handler: Optional[Callable] = None):
        self.command = command
        self.slack_app = slack_app
        self.base_handler = base_handler
        self.sub_commands: List[SubCommand] = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for sub_command in self.sub_commands:
            self._add_command(sub_command)
        self.slack_app.command(self.command)(self._default_handler)  # type: ignore

    def _add_command(self, sub_command: SubCommand) -> None:
        self.slack_app.command(  # type: ignore
            self.command,
            matchers=[_match_sub_command(sub_command)],
        )(sub_command.func)

    def _default_handler(self, command, ack):
        sub_command = command.get("text", "help").strip()
        if sub_command != "help":
            ack(unknown_sub_command(self.command, sub_command))
        else:
            ack(help(self.command, self.sub_commands))

    def on(self, text: str, help: Optional[str] = None) -> Callable:
        def decorator(func):
            self.sub_commands.append(
                SubCommand(
                    text=text,
                    func=func,
                    help=help,
                )
            )
            return func

        return decorator


class Api:
    def __init__(self):
        self.slack = App(process_before_response=True)
        self.slack_handler = SlackRequestHandler(self.slack)
        self.routes: Dict[str, Dict[str, Callable]] = defaultdict(dict)

    def route(self, path: str, methods: List[str]) -> Callable:
        def decorator(func: Callable) -> Callable:
            for method in methods:
                self.routes[path][method] = func
            return func

        return decorator

    def command(self, command: str) -> CommandBuilder:
        return CommandBuilder(command, self.slack)

    def handle(self, event: dict, context: dict) -> Any:
        request = map_api_request(event)
        if request.path == "/slack/event":
            return self.slack_handler.handle(event, context)
        handler = self._get_route_handler(request)
        if handler is None:
            return {"statusCode": 404}
        else:
            return map_api_response(handler(request))

    def _get_route_handler(self, request: ApiRequest) -> Optional[Callable]:
        if request.path not in self.routes:
            return None
        return self.routes[request.path].get(request.method)
