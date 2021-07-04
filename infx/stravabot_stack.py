from aws_cdk import core as cdk
from aws_cdk.aws_apigatewayv2 import (
    DomainMappingOptions,
    DomainName,
    HttpApi,
    HttpMethod,
)
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation
from aws_cdk.aws_dynamodb import Attribute, AttributeType, Table
from aws_cdk.aws_lambda import Tracing
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk.aws_sqs import Queue

from infx.config import (
    DOMAIN,
    JWT_SECRET_KEY,
    KV_KEY_RECORD,
    KV_TTL_RECORD,
    ROUTES,
    SLACK_BOT_TOKEN,
    SLACK_SIGNING_SECRET,
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
)


class StravabotStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        key_value_store = Table(
            self,
            "KeyValueStoreTable",
            partition_key=Attribute(
                name=KV_KEY_RECORD,
                type=AttributeType.STRING,
            ),
            time_to_live_attribute=KV_TTL_RECORD,
            read_capacity=1,
            write_capacity=1,
        )
        strava_event_queue = Queue(
            self,
            "StravaEventQueue",
            receive_message_wait_time=cdk.Duration.seconds(20),
        )
        certificate = Certificate(
            self,
            "Certificate",
            domain_name=DOMAIN,
            validation=CertificateValidation.from_dns(),
        )
        domain = DomainName(
            self,
            "Domain",
            domain_name=DOMAIN,
            certificate=certificate,
        )
        api = HttpApi(
            self,
            "Api",
            default_domain_mapping=DomainMappingOptions(
                domain_name=domain,
            ),
        )
        api_handler = PythonFunction(
            self,
            "ApiHandlerFunction",
            entry="./lambda",
            handler="handler",
            index="app.py",
            tracing=Tracing.ACTIVE,
            environment={
                "SLACK_BOT_TOKEN": SLACK_BOT_TOKEN,
                "SLACK_SIGNING_SECRET": SLACK_SIGNING_SECRET,
                "STRAVA_CLIENT_ID": STRAVA_CLIENT_ID,
                "STRAVA_CLIENT_SECRET": STRAVA_CLIENT_SECRET,
                "JWT_SECRET_KEY": JWT_SECRET_KEY,
                "KV_STORE_TABLE": key_value_store.table_name,
                "STRAVA_EVENT_QUEUE_URL": strava_event_queue.queue_url,
                "STRAVABOT_ENV": "prod",
            },
        )
        event_handler = PythonFunction(
            self,
            "EventHandlerFunction",
            entry="./lambda",
            handler="handler",
            index="events.py",
            tracing=Tracing.ACTIVE,
            environment={
                "SLACK_BOT_TOKEN": SLACK_BOT_TOKEN,
                "SLACK_SIGNING_SECRET": SLACK_SIGNING_SECRET,
                "STRAVA_CLIENT_ID": STRAVA_CLIENT_ID,
                "STRAVA_CLIENT_SECRET": STRAVA_CLIENT_SECRET,
                "JWT_SECRET_KEY": JWT_SECRET_KEY,
                "KV_STORE_TABLE": key_value_store.table_name,
                "STRAVABOT_ENV": "prod",
            },
        )
        event_handler.add_event_source(
            SqsEventSource(
                queue=strava_event_queue,
                batch_size=1,
            )
        )
        key_value_store.grant_read_write_data(api_handler)
        strava_event_queue.grant_send_messages(api_handler)
        integration = LambdaProxyIntegration(handler=api_handler)
        for methods, path in ROUTES:
            api.add_routes(path=path, methods=methods, integration=integration)
        api.add_routes(
            path="/slack/event",
            methods=[HttpMethod.POST],
            integration=integration,
        )
