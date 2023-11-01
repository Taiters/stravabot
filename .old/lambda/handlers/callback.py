from jinja2 import Environment, PackageLoader, select_autoescape

from stravabot.api import ApiRequest, api_endpoint
from stravabot.config import HOST

templates = Environment(
    loader=PackageLoader("stravabot"),
    autoescape=select_autoescape(),
)


@api_endpoint
def handler(request: ApiRequest) -> dict:
    template = templates.get_template("auth.html")
    return {
        "statusCode": 200,
        "body": template.render(
            host=HOST,
            parameters={
                "error": request.query_parameters.get("error"),
                "token": request.query_parameters.get("token"),
                "code": request.query_parameters.get("code"),
            },
        ),
        "headers": {
            "Content-Type": "text/html",
        },
    }
