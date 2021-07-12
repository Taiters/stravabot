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

from infx.config import BASE_ENVIRONMENT, DOMAIN, KV_KEY_RECORD, KV_TTL_RECORD, ROUTES
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
                "CDN_BUCKET": cdn_bucket.bucket_name,
            },
            timeout=cdk.Duration.seconds(10),
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
        cdn_bucket.grant_read_write(event_handler)

        api = Api(self, "Api", DOMAIN)
        with api.integration(LambdaProxyIntegration(handler=api_handler)) as integration:
            integration.add_route("/slack/event", [HttpMethod.POST])
            for methods, path in ROUTES:
                integration.add_route(path, methods)

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
