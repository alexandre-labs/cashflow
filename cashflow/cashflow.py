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
        return not self.__eq__(other)

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
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
