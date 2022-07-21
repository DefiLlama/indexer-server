#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from psycopg.sql import SQL, Identifier
from hexbytes import HexBytes

from lib.helpers.types import Chain, to_chain, Log

_query = "SELECT * FROM {0}.logs WHERE contract_address=%s"


def logs_to_contract_address(
    chain: Chain,
    contract_address: HexBytes,
):
    assert to_chain(chain)
    query = SQL(_query).format(Identifier(chain))

    return (query, [contract_address], Log)
    # return exec_psql_query(query, [contract_address], Log)
