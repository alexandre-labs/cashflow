import datetime
import decimal
import json
import uuid
from functools import singledispatch


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):

        for _type, handler in json_dumps.registry.items():

            if isinstance(obj, _type) and _type is not object:
                return handler(obj)

        return super(CustomEncoder, self).default(obj)


@singledispatch
def json_dumps(obj, **kwargs):
    return json.dumps(obj, cls=CustomEncoder, **kwargs)


@json_dumps.register(decimal.Decimal)
def encode_decimal(_decimal):
    return float(_decimal)


@json_dumps.register(datetime.date)
@json_dumps.register(datetime.datetime)
def encode_date_stuff(_date):
    return _date.isoformat()


@json_dumps.register(uuid.UUID)
def encode_uuid(_uuid):
    return str(_uuid)
