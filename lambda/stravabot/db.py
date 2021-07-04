from datetime import timedelta
from typing import Optional

from boto3_type_annotations.dynamodb import Table

from stravabot.utils import ttl_to_unixtime

KEY_FIELD = "record_key"
TTL_FIELD = "record_expiry"


class KeyValueStore:
    def __init__(self, table: Table):
        self.table = table

    def put(
        self,
        key: str,
        value: dict,
        ttl: Optional[timedelta] = None,
        expires: Optional[int] = None,
    ) -> None:
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

    def get(self, key: str) -> Optional[dict]:
        result = self.table.get_item(
            Key={
                KEY_FIELD: key,
            },
        )
        return result["Item"] if "Item" in result else None

    def delete(self, key: str) -> None:
        self.table.delete_item(
            Key={
                KEY_FIELD: key,
            },
        )
