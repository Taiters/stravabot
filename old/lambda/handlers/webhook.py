import os

import boto3

from stravabot.api import ApiRequest, api_endpoint

EVENT_FUNCTION = os.environ["STRAVA_EVENT_HANDLER"]
lambda_client = boto3.client("lambda")


@api_endpoint
def handler(request: ApiRequest) -> None:
    lambda_client.invoke(
        FunctionName=EVENT_FUNCTION,
        InvocationType="Event",
        Payload=request.body,
    )
