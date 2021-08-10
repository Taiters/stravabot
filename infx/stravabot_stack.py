from aws_cdk import core as cdk
from aws_cdk.aws_apigatewayv2 import HttpMethod
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_cloudfront import (
    AllowedMethods,
    BehaviorOptions,
    Distribution,
    PriceClass,
    ViewerProtocolPolicy,
)
from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_dynamodb import AttributeType
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket

from infx.config import BASE_ENVIRONMENT, DOMAIN, KV_KEY_RECORD, KV_TTL_RECORD
from infx.constructs.api import Api
from infx.constructs.cdn_certificate import CdnCertificate
from infx.constructs.handler import HandlerFunction
from infx.constructs.key_value_store import KeyValueStore


class StravabotStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        key_value_store = KeyValueStore(self, "KeyValueStore", KV_KEY_RECORD, KV_TTL_RECORD)
        key_value_store.index_field("slack_id", AttributeType.STRING)

        cdn_bucket = Bucket(self, "CdnBucket", block_public_access=BlockPublicAccess.BLOCK_ALL, enforce_ssl=True)

        BASE_ENVIRONMENT.update(
            {
                "KV_STORE_TABLE": key_value_store.table.table_name,
                "CDN_BUCKET": cdn_bucket.bucket_name,
            }
        )

        handler_function = HandlerFunction(
            self,
            id="HandlerFunction",
            src="./lambda",
            base_environment=BASE_ENVIRONMENT,
        )
        event_handler = handler_function.handler(
            "EventHandler",
            "handlers/event.py",
            "handler",
            timeout=cdk.Duration.seconds(30),
        )
        callback_handler = handler_function.handler(
            "CallbackHandler",
            "handlers/callback.py",
            "handler",
        )
        connect_handler = handler_function.handler(
            "ConnectHandler",
            "handlers/connect.py",
            "handler",
        )
        slack_handler = handler_function.handler(
            "SlackHandler",
            "handlers/slack.py",
            "handler",
        )
        verify_handler = handler_function.handler(
            "VerifyHandler",
            "handlers/verify.py",
            "handler",
        )
        webhook_handler = handler_function.handler(
            "WebhookHandler",
            "handlers/webhook.py",
            "handler",
            {
                "STRAVA_EVENT_HANDLER": event_handler.function_name,
            },
        )

        key_value_store.grant(event_handler)
        key_value_store.grant(connect_handler)
        key_value_store.grant(slack_handler)
        cdn_bucket.grant_read_write(event_handler)
        event_handler.grant_invoke(webhook_handler)

        api = Api(self, "Api", DOMAIN)
        api.integration(LambdaProxyIntegration(handler=callback_handler)).add_route("/strava/auth", [HttpMethod.GET])
        api.integration(LambdaProxyIntegration(handler=connect_handler)).add_route("/strava/auth", [HttpMethod.POST])
        api.integration(LambdaProxyIntegration(handler=verify_handler)).add_route("/strava/event", [HttpMethod.GET])
        api.integration(LambdaProxyIntegration(handler=webhook_handler)).add_route("/strava/event", [HttpMethod.POST])
        api.integration(LambdaProxyIntegration(handler=slack_handler)).add_route("/slack/event", [HttpMethod.POST])

        Distribution(
            self,
            "Distribution",
            price_class=PriceClass.PRICE_CLASS_100,
            domain_names=[f"cdn.{DOMAIN}"],
            certificate=Certificate.from_certificate_arn(
                self, "Certificate", CdnCertificate(self, "CdnCertificate").certificate_arn
            ),
            default_behavior=BehaviorOptions(
                origin=S3Origin(cdn_bucket),
                allowed_methods=AllowedMethods.ALLOW_GET_HEAD,
                viewer_protocol_policy=ViewerProtocolPolicy.HTTPS_ONLY,
            ),
        )
