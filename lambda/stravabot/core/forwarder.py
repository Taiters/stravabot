from boto3_type_annotations.lambda_ import Client

from stravabot.api import ApiRequest, ApiResponse


class ApiRequestForwarder:
    def __init__(self, lambda_name: str, lambda_client: Client):
        self.lambda_name = lambda_name
        self.lambda_client = lambda_client

    def __call__(self, request: ApiRequest) -> ApiResponse:
        self.lambda_client.invoke(
            FunctionName=self.lambda_name,
            InvocationType="Event",
            Payload=request.body,
        )
        return ApiResponse.ok()
