#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from psycopg.sql import SQL, Identifier
from hexbytes import HexBytes

from lib.helpers.types import Chain, to_chain, Transaction

_query = "SELECT * FROM {0}.transactions WHERE"


def txs_to_address(
    chain: Chain, from_address: Optional[HexBytes], to_address: Optional[HexBytes]
):
    assert to_chain(chain)
    if from_address is None and to_address is None:
        raise TypeError("from_address and to_address cannot be both None")

    params = []
    where = " "

    if from_address is not None:
        where += f"from_address = %s"
        params.append(from_address)

    if to_address is not None:
        if from_address is not None:
            where += " OR "

        where += f"to_address = %s"
        params.append(to_address)

    query = _query + where
    query = SQL(query).format(Identifier(chain))

    return (query, params, Transaction)
    # return exec_psql_query(query, params, Transaction)
