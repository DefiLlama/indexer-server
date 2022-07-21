#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from psycopg.sql import SQL, Identifier

from lib.helpers.types import Chain, to_chain, BlockNumber

_query = """
SELECT * FROM
(
  (SELECT number, timestamp FROM {0}.blocks 
    WHERE timestamp >= to_timestamp(%s)
    ORDER BY timestamp
    LIMIT 1)
  UNION ALL
  (SELECT number, timestamp FROM {0}.blocks
    WHERE timestamp < to_timestamp(%s)
    ORDER BY timestamp
    DESC LIMIT 1)
) as _
ORDER BY (to_timestamp(%s) - timestamp) LIMIT 1;
"""


def closest_timestamp_to_block(chain: Chain, timestamp: int):
    assert to_chain(chain)
    query = SQL(_query).format(Identifier(chain))

    return (query, [timestamp] * 3, BlockNumber)
