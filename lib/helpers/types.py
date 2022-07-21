#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Literal,
    _SpecialForm,
    cast,
    get_origin,
    get_args,
)
from dataclasses import dataclass
from datetime import datetime

from hexbytes import HexBytes

from aws_lambda_typing.events.api_gateway_proxy import APIGatewayProxyEventV2
from aws_lambda_typing.context import Context

# Alias
APIGatewayEvent = APIGatewayProxyEventV2
Context = Context

Chain = Literal["arbitrum", "avalanche", "bsc", "ethereum", "fantom", "polygon"]
_chains = get_args(Chain)


def to_chain(chain: Any) -> Union[Literal[False], Chain]:
    if chain not in _chains:
        return False

    return cast(Chain, chain)


class _Base:
    __dataclass_fields__: Dict[str, Any]

    def __post_init__(self) -> None:
        for field_name, field_def in self.__dataclass_fields__.items():
            if isinstance(field_def.type, _SpecialForm):
                # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                continue

            actual_type = get_origin(field_def.type) or field_def.type
            if isinstance(actual_type, _SpecialForm):
                # Case of typing.Union[…] or typing.ClassVar[…]
                actual_type = field_def.type.__args__

            actual_value = getattr(self, field_name)
            if type(actual_value) == bytes:
                # Convert bytes to Hexbytes
                actual_value = HexBytes(actual_value)
                setattr(self, field_name, actual_value)
                continue

            if field_name == "value":
                # Convert ETH values.
                if actual_value != 0:
                    actual_value /= Decimal("1e18")
                    setattr(self, field_name, actual_value)
                elif actual_value < 0:
                    raise TypeError(f"{actual_value=} is neg, {self}")

            try:
                ret = isinstance(actual_value, actual_type)
            except TypeError as e:
                if (
                    str(e)
                    != "Subscripted generics cannot be used with class and instance checks"
                ):
                    raise e

                continue

            if not ret:
                raise TypeError(
                    f"{field_name}: '{type(actual_value)}' instead of '{field_def.type}'"
                )

    def serialize(self) -> Tuple:
        ...


@dataclass
class Block(_Base):
    number: int
    hash: HexBytes
    difficulty: int
    total_difficulty: int
    miner: Optional[HexBytes]
    gas_limit: int
    gas_used: int
    timestamp: datetime
    base_fee_per_gas: int


@dataclass
class Transaction(_Base):
    block_number: int
    from_address: HexBytes
    to_address: HexBytes
    value: Decimal
    gas_used: int
    gas_price: int
    transaction_index: int
    hash: HexBytes
    transaction_type: int
    max_fee_per_gas: Optional[int]
    max_priority_fee_per_gas: Optional[int]
    input: Optional[HexBytes]
    input_decoded_named_args: Optional[bool]
    input_decoded: Optional[Union[Dict[str, Any], Tuple]]  # jsonb
    input_function_name: Optional[str]
    success: bool


@dataclass
class Log(_Base):
    transaction_hash: HexBytes
    contract_address: HexBytes
    log_index: int
    data: Optional[HexBytes]
    topics: List[HexBytes]
    event_decoded: Optional[str]
    data_decoded_named_args: Optional[bool]
    data_decoded: Optional[str]  # jsonb


@dataclass
class BlockNumber(_Base):
    number: int
    timestamp: datetime
