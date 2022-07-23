#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Handles cases where `input_decoded_named_args` is false which indicates the
ABI was found but not the exact verbpse function ABI found in the contract. This may 
happen if the code is a proxy or in a language other than Solidity, or my parser sucks..

We remedy this by explicitly providing the ABI for the function.

Example call:
    $ python3 scripts/alter_function_named_args.py \
        ethereum \
        0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7 \
        "exchange(int128 i, int128 j, uint256 dx, uint256 min_dy)"
"""

from typing import cast
import sys
import os

from psycopg.sql import SQL, Identifier
from psycopg.types.json import Jsonb
from hexbytes import HexBytes
from web3 import Web3

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from lib.helpers.postgres import get_psql_conn, exec_psql_query
from lib.helpers.types import Chain, Transaction, to_chain
from utils.aws import (
    get_abi_data,
    get_abi_data_contract,
    upload_abi_data,
    upload_abi_data_contract,
)

GET_NAMED_ARGS_FALSE_SQL = SQL(
    """
SELECT
    *
FROM
    {0}.transactions
WHERE
    to_address = %s
    AND NOT input_decoded_named_args
    AND input_function_name = %s;
"""
)

UPDATE_NAMED_ARG_SQL = SQL(
    """
UPDATE
    {0}.transactions
SET
    input_decoded_named_args = true,
    input_decoded = %s
WHERE
    hash = %s
RETURNING hash;
"""
)


def handle(chain: Chain, address: HexBytes, func: str, function_sig: HexBytes):
    _chain = Identifier(chain)
    query = GET_NAMED_ARGS_FALSE_SQL.format(_chain)
    update_query = UPDATE_NAMED_ARG_SQL.format(_chain)
    func_name, rest = func.split("(")

    def __map(x: str):
        _x = x.strip().rstrip().split(" ")
        return _x[-1]  # (name)

    args = list(map(__map, rest.split(")")[0].split(",")))
    ret = exec_psql_query(query, [address, func_name], Transaction)

    with get_psql_conn() as c:
        for x in ret:
            assert x.input is not None and x.input_decoded is not None
            assert x.input[:4] == function_sig, "incorrect function input"
            assert len(x.input_decoded) == len(args), "incorrect arg length"

            x.input_decoded = cast(tuple, x.input_decoded)
            x.input_decoded = dict(zip(args, x.input_decoded))
            print(x.hash.hex(), x.input_decoded)

            c.execute(update_query, [Jsonb(x.input_decoded), x.hash])


if __name__ == "__main__":
    _, chain, address, func = sys.argv

    func_name, rest = func.split("(")
    types = map(lambda x: x.strip().rstrip().split(" ")[0], rest.split(","))
    function_abi = f'{func_name}({",".join( types)})'

    assert (chain := to_chain(chain)), "invalid chain"
    function_sig = Web3.keccak(text=function_abi)[:4]
    address = HexBytes(address)
    _address = address.hex()

    if get_abi_data_contract("function", function_sig, chain, _address) is None:
        print("uploading", chain, _address, function_sig.hex(), func)
        upload_abi_data_contract("function", function_sig, func, chain, _address)

    if get_abi_data("function", function_sig) is None:
        print("uploading", function_sig.hex(), function_abi)
        upload_abi_data("function", function_sig, function_abi)

    handle(chain, address, func, function_sig)
