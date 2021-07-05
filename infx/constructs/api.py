from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, List

from aws_cdk import core as cdk
from aws_cdk.aws_apigatewayv2 import (
    DomainMappingOptions,
    DomainName,
    HttpApi,
    HttpMethod,
    IHttpRouteIntegration,
)
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation


class IntegrationBuilder(AbstractContextManager):
    def __init__(self, api: HttpApi, integration: IHttpRouteIntegration):
        super().__init__()
        self.api = api
        self.integration = integration

    def add_route(self, path: str, methods: List[HttpMethod]) -> None:
        self.api.add_routes(path=path, methods=methods, integration=self.integration)

    def __enter__(self) -> IntegrationBuilder:
        return super().__enter__()

    def __exit__(self, *args: Any) -> None:
        super().__exit__(*args)


class Api(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, domain: str):
        super().__init__(scope, id)
        self.api = HttpApi(
            self,
            "Api",
            default_domain_mapping=DomainMappingOptions(
                domain_name=DomainName(
                    self,
                    "Domain",
                    domain_name=domain,
                    certificate=Certificate(
                        self,
                        "Certificate",
                        domain_name=domain,
                        validation=CertificateValidation.from_dns(),
                    ),
                )
            ),
        )

    def integration(self, integration: IHttpRouteIntegration) -> IntegrationBuilder:
        return IntegrationBuilder(self.api, integration)
