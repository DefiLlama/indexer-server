#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple

from psycopg.sql import SQL, Identifier
from hexbytes import HexBytes

from lib.helpers.postgres import exec_psql_query
from lib.helpers.types import Chain, to_chain


_held_nft_ids_query = SQL(
    """
SELECT
    data_decoded->>'tokenId'
FROM
    {0}.logs
WHERE
    contract_address = %(contract)s
    AND event_decoded = 'Transfer'
    AND data_decoded->>'from' = '0x0000000000000000000000000000000000000000'
    AND data_decoded->>'to' = %(user)s
EXCEPT
SELECT
    data_decoded->>'tokenId'
FROM
    {1}.logs
WHERE
    contract_address = %(contract)s
    AND event_decoded = 'Transfer'
    AND data_decoded->>'from' = %(user)s
"""
)


def exec_held_nft_ids_to_address(
    chain: Chain, contract: HexBytes, user: HexBytes
) -> Tuple[str, ...]:
    assert to_chain(chain)

    _chain = Identifier(chain)
    query = _held_nft_ids_query.format(_chain, _chain)

    ret = exec_psql_query(query, {"contract": contract, "user": user.hex()})
    # [('349',)]
    return ret[0]
