from datetime import timedelta

import pytest
from boto3.dynamodb.conditions import Key

from stravabot.db import KeyValueStore, KeyValueStoreIndex


@pytest.fixture
def table(mocker):
    return mocker.Mock()


@pytest.fixture
def store(table):
    return KeyValueStore(table)


def test_put_passes_expected_values_to_table(store, table):
    store.put(
        key="a_key",
        value={"some": "data"},
    )
    table.put_item.assert_called_once()
    assert table.put_item.call_args[1]["Item"] == {
        "record_key": "a_key",
        "some": "data",
    }


def test_put_sets_expected_expiry_field_from_ttl_param(freezer, store, table):
    freezer.move_to("2021-01-01T00:00:00")
    store.put(
        key="key",
        value={"a": "value"},
        ttl=timedelta(days=1, seconds=23),
    )
    table.put_item.assert_called_once()
    assert table.put_item.call_args[1]["Item"] == {
        "record_key": "key",
        "record_expiry": 1609545623,
        "a": "value",
    }


def test_put_sets_expected_expiry_field_from_expires_param(store, table):
    store.put(
        key="key",
        value={"a": "value"},
        expires=12345,
    )
    table.put_item.assert_called_once()
    assert table.put_item.call_args[1]["Item"] == {
        "record_key": "key",
        "record_expiry": 12345,
        "a": "value",
    }


def test_get_passes_expected_key_to_table(store, table):
    table.get_item.return_value = {}
    store.get("a-key")
    table.get_item.assert_called_once_with(Key={"record_key": "a-key"}, ConsistentRead=False)


def test_get_passes_consistent_read_value_to_table(store, table):
    table.get_item.return_value = {}
    store.get("a-key", consistent_read=True)
    table.get_item.assert_called_once_with(Key={"record_key": "a-key"}, ConsistentRead=True)


def test_get_returns_item_from_result(store, table):
    table.get_item.return_value = {"Item": "the-item"}
    result = store.get("foo")
    assert result == "the-item"


def test_get_returns_none_if_item_is_not_present(store, table):
    table.get_item.return_value = {"Something": "else"}
    result = store.get("foo")
    assert result is None


def test_get_with_index_calls_expected_index(store, table):
    table.query.return_value = {}
    store.get("a-key", index=KeyValueStoreIndex.SLACK_ID)
    table.query.assert_called_once_with(
        IndexName="slack_id", KeyConditionExpression=Key("slack_id").eq("a-key"), ConsistentRead=False
    )


def test_get_with_index_passes_consistent_read_value_to_table(store, table):
    table.query.return_value = {}
    store.get("a-key", index=KeyValueStoreIndex.SLACK_ID, consistent_read=True)
    table.query.assert_called_once_with(
        IndexName="slack_id", KeyConditionExpression=Key("slack_id").eq("a-key"), ConsistentRead=True
    )


def test_get_with_index_returns_item_from_result(store, table):
    table.query.return_value = {"Items": ["an-item"]}
    result = store.get("a-key", index=KeyValueStoreIndex.SLACK_ID)
    assert result == "an-item"


def test_get_with_index_returns_none_if_items_are_empty(store, table):
    table.query.return_value = {"Items": []}
    result = store.get("a-key", index=KeyValueStoreIndex.SLACK_ID)
    assert result is None


def test_get_with_index_returns_none_if_items_is_not_present(store, table):
    table.query.return_value = {"Something": "Else"}
    result = store.get("a-key", index=KeyValueStoreIndex.SLACK_ID)
    assert result is None
