from datetime import timedelta
from enum import Enum
from typing import Optional

from boto3.dynamodb.conditions import Key
from boto3_type_annotations.dynamodb import Table

from stravabot.utils import ttl_to_unixtime

KEY_FIELD = "record_key"
TTL_FIELD = "record_expiry"


class KeyValueStoreIndex(Enum):
    SLACK_ID = "slack_id"


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

    def get(
        self, key: str, index: Optional[KeyValueStoreIndex] = None, consistent_read: bool = False
    ) -> Optional[dict]:
        if index:
            return self._get_from_index(key, index, consistent_read)
        return self._get_from_table(key, consistent_read)

    def delete(self, key: str) -> None:
        self.table.delete_item(
            Key={
                KEY_FIELD: key,
            },
        )

    def _get_from_table(self, key: str, consistent_read: bool = False) -> Optional[dict]:
        result = self.table.get_item(
            Key={
                KEY_FIELD: key,
            },
            ConsistentRead=consistent_read,
        )
        return result["Item"] if "Item" in result else None

    def _get_from_index(self, key: str, index: KeyValueStoreIndex, consistent_read: bool = False) -> Optional[dict]:
        result = self.table.query(
            IndexName=index.value, KeyConditionExpression=Key(index.value).eq(key), ConsistentRead=consistent_read
        )
        if "Items" in result and result["Items"]:
            return result["Items"][0]
        return None
