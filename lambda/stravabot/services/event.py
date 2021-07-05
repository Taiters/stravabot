from boto3_type_annotations.lambda_ import Client


class EventService:
    def __init__(self, lambda_name: str, lambda_client: Client):
        self.lambda_name = lambda_name
        self.lambda_client = lambda_client

    def send_event(self, event: str) -> None:
        self.lambda_client.invoke(
            FunctionName=self.lambda_name,
            InvocationType="Event",
            Payload=event,
        )
