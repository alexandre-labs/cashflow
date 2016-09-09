# -*- coding: utf-8 -*-

import datetime
import decimal
import math
import unittest

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.datetime import datetimes
import hypothesis.strategies as s
import pytest

from cashflow import cashflow
from cashflow.utils import serialize as serialize_utils


TransactionStrategy = s.builds(
    cashflow.Transaction,
    st.decimals(),
    datetimes(),
    st.dictionaries(keys=st.text(), values=st.uuids())
)


class TransactionTestCase(unittest.TestCase):

    @given(st.decimals(), datetimes(),
           st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_get_transaction_value(self, value, timestamp, metadata):

        transaction = cashflow.Transaction(value, timestamp, metadata)

        if math.isnan(value):
            assert math.isnan(transaction.value)
        else:
            assert transaction.value == value

    @given(st.decimals(), datetimes(),
           st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_get_transaction_timestamp(self, value, timestamp, metadata):

        transaction = cashflow.Transaction(value, timestamp, metadata)

        assert transaction.timestamp == timestamp

    @given(st.decimals(), datetimes(),
           st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_get_transaction_metadata(self, value, timestamp, metadata):

        transaction = cashflow.Transaction(value, timestamp, metadata)

        assert transaction.metadata == metadata

    @given(st.decimals(), datetimes(),
           st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_transaction_serialization(self, value, timestamp, metadata):

        transaction = cashflow.Transaction(value, timestamp, metadata)
        serialized_data = transaction.serialize()

        expected_data = {
            'value': transaction.value,
            'timestamp': transaction.timestamp,
            'metadata': transaction.metadata
        }

        assert expected_data == serialized_data

    @given(st.decimals(), st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_compare_two_transactions(self, value, metadata):

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
    def test_compare_transaction_to_other_object(self, value, timestamp, metadata):  # noqa

        transaction = cashflow.Transaction(value, timestamp, metadata)

        with pytest.raises(RuntimeError) as cm:
            transaction == 'foo bar baz'

        expected_message = '{!r} is not an instance of Transaction'.format(
            'foo bar baz'
        )

        assert str(cm.value) == expected_message


class CashFlowTestCase(unittest.TestCase):

    @given(st.tuples(TransactionStrategy))
    def test_dunder_len(self, transactions):

        cf = cashflow.CashFlow(transactions=transactions)

        assert len(cf) == len(transactions)

    @given(st.tuples(TransactionStrategy))
    def test_dunder_iter(self, transactions):

        cf = cashflow.CashFlow(transactions=transactions)

        for transaction in cf:
            assert transaction in transactions

    @given(st.tuples(TransactionStrategy))
    def test_dunder_contains(self, transactions):

        cf = cashflow.CashFlow(transactions=transactions)

        self.assertIn(transactions[0], cf)

    @given(st.tuples(TransactionStrategy))
    def test_dunder_getitem(self, transactions):

        cf = cashflow.CashFlow()

        with pytest.raises(IndexError):
            cf[0]

        assert len(cf[0:100]) == 0

        for transaction in transactions:
            cf.append(transaction)

        assert tuple(cf[0].transactions)[0] == transactions[0]

        assert tuple(cf[0:5].transactions) == transactions[0:5]
        assert len(tuple(cf[0:5].transactions)) == len(transactions[0:5])

        assert tuple(cf[::-1].transactions) == tuple(reversed(transactions))
        assert len(tuple(cf[::-1].transactions)) == len(transactions[::-1])

    @given(st.tuples(TransactionStrategy))
    def test_net_value(self, transactions):

        assume(all(not math.isnan(t.value) for t in transactions))

        cf = cashflow.CashFlow(transactions=transactions)

        self.assertAlmostEqual(
            cf.net_value, sum(t.value for t in transactions)
        )

    @given(TransactionStrategy)
    def test_append_duplicate_transaction(self, transaction):

        cf = cashflow.CashFlow()

        cf.append(transaction)

        with pytest.raises(ValueError) as cm:
            cf.append(transaction)

        expected_message = (
            '{} already added to the cash flow'.format(repr(transaction))
            )

        assert str(cm.value) == expected_message

    def test_create_an_empty_cashflow(self):

        cf = cashflow.CashFlow()

        assert len(cf) == 0

        assert list(cf.transactions) == []

        assert cf.net_value == decimal.Decimal(0)

    @given(TransactionStrategy)
    def test_cash_flow_with_one_transaction(self, transaction):

        assume(not math.isnan(transaction.value))

        cf = cashflow.CashFlow()

        cf.append(transaction)

        assert len(cf) == 1

        assert tuple(cf.transactions) == (transaction, )

        self.assertAlmostEqual(
            cf.net_value, sum(t.value for t in (transaction,))
        )

    @given(st.tuples(TransactionStrategy))
    def test_cash_flow_filter_example_simple_predicate(self, transactions):

        assume(all(not math.isnan(t.value) for t in transactions))
        assume(all(transaction.value > 0 for transaction in transactions))

        cf = cashflow.CashFlow(transactions=transactions)

        assert len(cf.filter(lambda t: t.value > 0)) == len(transactions)

    @given(st.tuples(TransactionStrategy))
    def test_cash_flow_filter_composition(self, transactions):

        assume(all(not math.isnan(t.value) for t in transactions))
        assume(all(0 < t.value <= 100 for t in transactions))

        cf = cashflow.CashFlow(transactions=transactions).filter(
            lambda t: t.value > 0
        )

        assert len(cf) == len(transactions)

        # Duplicate the filter to ensure the value keeps the same
        cf = cf.filter(lambda t: t.value > 0).filter(lambda t: t.value > 0)

        assert len(cf) == len(transactions)

        cf = cf.filter(lambda t: t.value == 100)

        transactions_values_greater_than_100 = tuple(
            t for t in transactions if t.value == 100
        )

        assert tuple(cf.transactions) == transactions_values_greater_than_100

    @given(st.tuples(TransactionStrategy))
    def test_seriaize_cash_flow(self, transactions):

        cf = cashflow.CashFlow(transactions=transactions)

        expected_data = {'cashflow': [t.serialize() for t in transactions]}

        self.assertDictEqual(cf.serialize(), expected_data)

        self.assertEqual(
            serialize_utils.json_dumps(cf.serialize()),
            serialize_utils.json_dumps(expected_data)
        )
