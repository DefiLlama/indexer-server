#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, cast
from collections import defaultdict
import os

from boto3.dynamodb.conditions import Key
from hexbytes import HexBytes
import boto3

abi_table = boto3.resource("dynamodb").Table(os.environ["AWS_DDB_ABI_DECODER"])


def upload_abi_data(_type: str, signature: HexBytes, abi_method: str) -> None:
    assert _type in ["function", "event"]

    assert (
        abi_table.put_item(
            Item={
                "PK": f"{_type}#{signature.hex()}",
                "SK": abi_method,
            }
        )["ResponseMetadata"]["HTTPStatusCode"]
        == 200
    ), "put_item failed"


def upload_abi_data_contract(
    _type: str,
    signature: HexBytes,
    verbose_abi: str,  # ABI with argument names.
    chain: str,
    address: str,
) -> None:
    assert _type in ["function", "event"]

    assert (
        abi_table.put_item(
            Item={
                "PK": f"contract#{chain.lower()}#{address.lower()}",
                "SK": f"{_type}#{signature.hex()}",
                "verbose_abi": verbose_abi,
            }
        )["ResponseMetadata"]["HTTPStatusCode"]
        == 200
    ), "put_item failed"


def get_abi_data(_type: str, signature: HexBytes):
    assert _type in ["function", "event"]

    if _type == "function":
        assert len(signature) == 4  # Function selector.
    elif _type == "event":
        assert len(signature) == 32  # Topic hash.

    res: Dict[str, List[str]] = defaultdict(list)

    ret = abi_table.query(
        KeyConditionExpression=Key("PK").eq(f"{_type}#{signature.hex()}")
    )

    if _type == "event":
        # If more than 1 then there is a colliso - uh oh.
        assert ret["Count"] <= 1

        if ret["Count"] != 0:
            item = ret["Items"][0]
            sig = cast(str, item["PK"]).split("#")[1]

            return {sig: item["SK"]}

        return {}
    elif _type == "function":
        if ret["Count"] != 0:
            for item in ret["Items"]:
                sig = cast(str, item["PK"]).split("#")[1]
                res[sig].append(cast(str, item["SK"]))

    return res


def get_abi_data_contract(
    _type: str, signature: HexBytes, chain: str, address: str
) -> Optional[Dict[str, str]]:
    assert _type in ["function", "event"]

    if _type == "function":
        assert len(signature) == 4  # Function selector.
    elif _type == "event":
        assert len(signature) == 32  # Topic hash.

    ret = abi_table.query(
        KeyConditionExpression=Key("PK").eq(
            f"contract#{chain.lower()}#{address.lower()}"
        )
        & Key("SK").eq(f"{_type}#{signature.hex()}")
    )

    # Should only be no more than 1 result for both functions and events.
    assert ret["Count"] <= 1

    if ret["Count"] != 0:
        item = ret["Items"][0]
        sig = cast(str, item["SK"]).split("#")[1]

        return {sig: cast(str, item["verbose_abi"])}
