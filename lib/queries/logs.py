#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from psycopg.sql import SQL, Identifier
from hexbytes import HexBytes

from lib.helpers.types import Chain, to_chain, Log

_query = "SELECT * FROM {0}.logs WHERE contract_address = %s"


def logs_to_contract_address(
    chain: Chain,
    contract_address: HexBytes,
    topic0: Optional[HexBytes],
    txhash: Optional[HexBytes],
):
    assert to_chain(chain)
    print(topic0, txhash)
    params = [contract_address]
    where = " "

    if txhash is not None:
        where += "AND transaction_hash = %s "
        params.append(txhash)

    if topic0 is not None:
        where += "AND topics[1] = %s"
        params.append(topic0)

    query = _query + where
    query = SQL(query).format(Identifier(chain))

    return (query, params, Log)
    # return exec_psql_query(query, [contract_address], Log)
