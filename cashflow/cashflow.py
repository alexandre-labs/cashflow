# -*- coding: utf-8 -*-

import math


class Transaction(object):

    ''' A transaction is a register of an amount in a cash flow. It is
    basically a value and a timestamp.'''

    def __init__(self, value, timestamp, metadata):

        '''
        :value: decimal.Decimal object
        :timestamp: datetime.datetime object
        :metadata: dict object.
        '''

        self._value = value
        self._timestamp = timestamp
        self._metadata = metadata

    def __repr__(self):
        return 'Transaction({}, {}, {})'.format(
            self.value, self.timestamp, self.metadata
        )

    def __eq__(self, other):

        if not isinstance(other, Transaction):
            raise RuntimeError('{!r} is not an instance of Transaction'.format(
                other
            ))

        return all([
            (self.value == other.value) or
            (math.isnan(self.value) and math.isnan(other.value)),
            self.timestamp == other.timestamp,
            self.metadata == other.metadata
        ])

    def __ne__(self, other):
        return not (self == other)

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def metadata(self):
        return self._metadata

    def serialize(self):
        return {
            'value': self.value,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }


class CashFlow(object):

    ''' A Cash Flow is just a list of transaction (Obvious, Captain) '''

    def __init__(self, transactions=None):
        self._transactions = tuple()

        for t in (transactions or tuple()):
            self.append(t)

    def __contains__(self, other_transaction):
        return any(transaction == other_transaction for transaction in self)

    def __iter__(self):
        yield from self._transactions

    def __getitem__(self, item):
        if isinstance(item, int):
            return CashFlow(transactions=(self._transactions[item], ))
        return CashFlow(transactions=self._transactions[item])

    def __len__(self):
        return len(self._transactions)

    @property
    def transactions(self):
        yield from self

    @property
    def net_value(self):
        return sum(transaction.value for transaction in self)

    def append(self, transaction):

        if transaction in self:

            raise ValueError(
                '{} already added to the cash flow'.format(repr(transaction))
            )

        self._transactions += (transaction, )

    def filter(self, predicate):
        return CashFlow(transactions=filter(predicate, self._transactions))

    def serialize(self):
        return {'cashflow': [transaction.serialize() for transaction in self]}
