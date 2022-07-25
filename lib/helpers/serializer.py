#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from typing import Any
import json

from hexbytes import HexBytes

from lib.helpers.types import _Base


class CustomJSONEncoder(json.JSONEncoder):
    def _transform(self, v):
        if isinstance(v, bytes):
            return HexBytes(v).hex()
        elif isinstance(v, HexBytes):
            return v.hex()
        elif isinstance(v, Decimal):
            return str(v)
        elif isinstance(v, int):
            # Over max `Number.MAX_SAFE_INTEGER` for JS.
            if v > (2**53 - 1):
                return str(v)
        elif isinstance(v, datetime):
            return int(v.timestamp())

        return v

    def default(self, o):
        if isinstance(o, _Base):
            return {k: self._transform(v) for k, v in o.__dict__.items()}
        else:
            ret = self._transform(o)
            if o != ret:
                return ret

        super().default(o)

    def encode(self, o):
        if isinstance(o, dict):
            o = {self._transform(k): self._transform(v) for k, v in o.items()}

        return super().encode(o)


class Request:
    @staticmethod
    def parse(data: str):
        return json.loads(data)


class Response:
    @staticmethod
    def make_response(data: Any, status: int = 200):
        return {
            "statusCode": status,
            "body": json.dumps(data, cls=CustomJSONEncoder),
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*",
                "access-control-allow-headers": "*",
            },
        }

    @staticmethod
    def make_bad_request(data: str):
        return Response.make_response({"error": data}, status=400)
