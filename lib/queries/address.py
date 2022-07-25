#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from typing import Optional, Tuple
from decimal import Decimal

from psycopg.sql import SQL, Identifier
from hexbytes import HexBytes

from lib.helpers.types import Chain, to_chain, Transaction, Approval
from lib.helpers.postgres import exec_psql_query

_query = "SELECT * FROM {0}.transactions WHERE"
_approvals_query = SQL(
    """
SELECT
    contract_address,
    data_decoded->>'spender' AS "spender",
    (data_decoded->>'value')::numeric AS "value"
FROM
    {0}.logs
WHERE
    event_decoded = 'Approval'
    AND topics[4] IS NULL /* erc20 */
    AND data_decoded->>'owner' = %s;
"""
)


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


def exec_approvals_to_address(chain: Chain, address: HexBytes):
    assert to_chain(chain)
    query = _approvals_query.format(Identifier(chain))

    ret = exec_psql_query(query, [address.hex()], Approval)
    contract_addresses = defaultdict(lambda: defaultdict(Decimal))

    # Handle Approvals of 0 (revoked approval).
    for x in ret:
        if x.value != 0:
            contract_addresses[x.contract_address][x.spender] += x.value
        else:
            contract_addresses[x.contract_address][x.spender] = Decimal()

    return contract_addresses
