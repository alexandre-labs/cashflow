# -*- coding: utf-8 -*-

import datetime
import math

from hypothesis import given, strategies as st
from hypothesis.extra.datetime import datetimes
import pytest

from cashflow import cashflow


@given(st.decimals(), datetimes(),
       st.dictionaries(keys=st.text(), values=st.uuids()))
def test_get_transaction_value(value, timestamp, metadata):

    transaction = cashflow.Transaction(value, timestamp, metadata)

    if math.isnan(value):
        assert math.isnan(transaction.value)
    else:
        assert transaction.value == value


@given(st.decimals(), datetimes(),
       st.dictionaries(keys=st.text(), values=st.uuids()))
def test_get_transaction_timestamp(value, timestamp, metadata):

    transaction = cashflow.Transaction(value, timestamp, metadata)

    assert transaction.timestamp == timestamp


@given(st.decimals(), datetimes(),
       st.dictionaries(keys=st.text(), values=st.uuids()))
def test_get_transaction_metadata(value, timestamp, metadata):

    transaction = cashflow.Transaction(value, timestamp, metadata)

    assert transaction.metadata == metadata


@given(st.decimals(), datetimes(),
       st.dictionaries(keys=st.text(), values=st.uuids()))
def test_transaction_serialization(value, timestamp, metadata):

    transaction = cashflow.Transaction(value, timestamp, metadata)
    serialized_data = transaction.serialize()

    expected_data = {
        'value': transaction.value,
        'timestamp': transaction.timestamp.isoformat(),
        'metadata': transaction.metadata
    }

    assert expected_data == serialized_data


@given(st.decimals(), st.dictionaries(keys=st.text(), values=st.uuids()))
def test_compare_two_transactions(value, metadata):

    # The difference is the timestamp...
    transaction1 = cashflow.Transaction(
        value, datetime.datetime.now(), metadata
    )
    transaction2 = cashflow.Transaction(
        value, datetime.datetime.now(), metadata
    )

    assert transaction1 == transaction1
    assert transaction1 != transaction2

    # Using date instead datetime to ensure different objects with the same
    # data will be considered as equal.
    transaction1 = cashflow.Transaction(
        value, datetime.date.today(), metadata
    )
    transaction2 = cashflow.Transaction(
        value, datetime.date.today(), metadata
    )

    assert transaction1 == transaction1
    assert transaction1 == transaction2


@given(st.decimals(), datetimes(),
       st.dictionaries(keys=st.text(), values=st.uuids()))
def test_compare_transaction_with_any_other_object(value, timestamp, metadata):

    transaction = cashflow.Transaction(value, timestamp, metadata)

    with pytest.raises(RuntimeError) as cm:
        transaction == 'foo bar baz'

    expected_message = '{!r} is not an instance of Transaction'.format(
        'foo bar baz'
    )

    assert str(cm.value) == expected_message
