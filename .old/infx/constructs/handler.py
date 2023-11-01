from typing import Dict, Optional

from aws_cdk import core as cdk
from aws_cdk.aws_lambda import Tracing
from aws_cdk.aws_lambda_python import PythonFunction


class HandlerFunction(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, src: str, base_environment: Dict[str, str]):
        super().__init__(scope, id)
        self.src = src
        self.base_environment = base_environment

    def handler(
        self,
        name: str,
        index: str,
        handler: str,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[cdk.Duration] = None,
    ) -> PythonFunction:
        environment = self.base_environment.copy()
        if env:
            environment.update(env)
        return PythonFunction(
            self,
            name,
            entry=self.src,
            index=index,
            handler=handler,
            tracing=Tracing.ACTIVE,
            environment=environment,
            timeout=timeout,
        )
