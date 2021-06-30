from datetime import timedelta
from typing import Optional
import boto3

from stravabot.config import KV_STORE_TABLE
from stravabot.utils import ttl_to_unixtime


KEY_FIELD = "record_key"
TTL_FIELD = "record_expiry"


class KeyValueStore:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(KV_STORE_TABLE)

    def put(
        self,
        key: str,
        value: dict,
        ttl: Optional[timedelta] = None,
        expires: Optional[int] = None,
    ):
        expiry = None
        if ttl:
            expiry = ttl_to_unixtime(ttl)
        elif expires:
            expiry = expires
        item = value.copy()
        item[KEY_FIELD] = key
        if expiry:
            item[TTL_FIELD] = expiry

        self.table.put_item(
            Item=item,
            ReturnValues="NONE",
        )

    def get(self, key):
        result = self.table.get_item(
            Key={
                KEY_FIELD: key,
            },
        )
        return result["Item"] if "Item" in result else None
