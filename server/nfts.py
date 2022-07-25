#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.helpers.types import APIGatewayEvent, Context, to_chain
from lib.queries.nfts import exec_held_nft_ids_to_address
from lib.helpers.hexbytes import try_hexbytes
from lib.helpers.serializer import Response


def user_held_nfts(event: APIGatewayEvent, context: Context):
    contract = None
    chain = None
    user = None

    if (ev := event.get("pathParameters")) is not None:
        contract = try_hexbytes(ev.get("contract"))
        user = try_hexbytes(ev.get("user"))
        chain = ev.get("chain")

    if not (chain := to_chain(chain)):
        return Response.make_bad_request(f"`chain` is invalid")
    elif contract is None or user is None:
        return Response.make_bad_request("`contract` or `user` is null")

    return Response.make_response(
        exec_held_nft_ids_to_address(chain, contract, user),
    )
