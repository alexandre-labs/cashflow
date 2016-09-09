# -*- coding: utf-8 -*-

import json
import unittest

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.datetime import datetimes
import pytest

from cashflow.utils import serialize as serialize_utils


class CustomJSONEncoderTestCase(unittest.TestCase):

    @given(st.dictionaries(keys=st.text(), values=st.text()))
    def test_encoder_with_text(self, data):
        assert serialize_utils.json_dumps(data) == json.dumps(data)

    @given(st.dictionaries(keys=st.integers(), values=st.integers()))
    def test_encode_with_integers(self, data):
        assert serialize_utils.json_dumps(data) == json.dumps(data)

    @given(st.dictionaries(keys=st.text(), values=st.uuids()))
    def test_encode_with_uuids(self, data):

        assume(data != {})

        with pytest.raises(TypeError):
            json.dumps(data)

        serialize_utils.json_dumps(data)

    @given(st.dictionaries(keys=st.text(), values=datetimes()))
    def test_encode_with_datetimes(self, data):

        assume(data != {})

        with pytest.raises(TypeError):
            json.dumps(data)

        serialize_utils.json_dumps(data)
