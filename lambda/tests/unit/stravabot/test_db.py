from datetime import timedelta

import pytest

from stravabot.db import KeyValueStore


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
    table.get_item.assert_called_once_with(Key={"record_key": "a-key"})


def test_get_returns_item_from_result(store, table):
    table.get_item.return_value = {"Item": "the-item"}
    result = store.get("foo")
    assert result == "the-item"


def test_get_returns_none_if_item_is_not_present(store, table):
    table.get_item.return_value = {"Something": "else"}
    result = store.get("foo")
    assert result is None
