from boto3_type_annotations.sqs import Queue

from stravabot.api import ApiRequest, ApiResponse


class ApiRequestForwarder:
    def __init__(self, queue: Queue):
        self.queue = queue

    def __call__(self, request: ApiRequest) -> ApiResponse:
        self.queue.send_message(
            MessageBody=request.body,
        )
        return ApiResponse.ok()
