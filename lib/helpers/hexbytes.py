#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Optional

from hexbytes import HexBytes


def try_hexbytes(hexstr: Any) -> Optional[HexBytes]:
    if hexstr is None or not isinstance(hexstr, (bool, bytearray, bytes, int, str)):
        return None

    return HexBytes(hexstr)
