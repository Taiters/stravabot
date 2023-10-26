from __future__ import annotations

from aws_cdk import core as cdk
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_iam import IGrantable


class KeyValueStore(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, key_record: str, ttl_record: str):
        super().__init__(scope, id)
        self.table = Table(
            self,
            "Table",
            partition_key=Attribute(
                name=key_record,
                type=AttributeType.STRING,
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute=ttl_record,
        )

    def index_field(self, field_name: str, field_type: AttributeType) -> None:
        self.table.add_global_secondary_index(
            index_name=field_name, partition_key=Attribute(name=field_name, type=field_type)
        )

    def grant(self, grantee: IGrantable) -> None:
        self.table.grant_read_write_data(grantee)
