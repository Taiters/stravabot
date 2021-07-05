from aws_cdk import core as cdk
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_dynamodb import AttributeType

from infx.config import BASE_ENVIRONMENT, DOMAIN, KV_KEY_RECORD, KV_TTL_RECORD, ROUTES
from infx.constructs.api import Api
from infx.constructs.handler import HandlerFunction
from infx.constructs.key_value_store import KeyValueStore


class StravabotStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        key_value_store = KeyValueStore(self, "KeyValueStore", KV_KEY_RECORD, KV_TTL_RECORD)
        key_value_store.index_field("slack_id", AttributeType.STRING)

        handler_function = HandlerFunction(
            self,
            id="HandlerFunction",
            src="./lambda",
            base_environment=BASE_ENVIRONMENT,
        )
        event_handler = handler_function.handler(
            "EventHandler",
            "events.py",
            "handler",
            {
                "KV_STORE_TABLE": key_value_store.table.table_name,
            },
        )
        api_handler = handler_function.handler(
            "ApiHandler",
            "app.py",
            "handler",
            {
                "KV_STORE_TABLE": key_value_store.table.table_name,
                "STRAVA_EVENT_HANDLER": event_handler.function_name,
            },
        )

        event_handler.grant_invoke(api_handler)
        key_value_store.grant(event_handler)
        key_value_store.grant(api_handler)

        api = Api(self, "Api", DOMAIN)
        with api.integration(LambdaProxyIntegration(handler=api_handler)) as integration:
            integration.add_route("/slack/event", [HttpMethod.POST])
            for methods, path in ROUTES:
                integration.add_route(path, methods)
