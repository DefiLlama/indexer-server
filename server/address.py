#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.helpers.types import APIGatewayEvent, Context, to_chain
from lib.helpers.paginate import exec_paginate_query
from lib.queries.address import txs_to_address
from lib.helpers.hexbytes import try_hexbytes
from lib.helpers.serializer import Response


def address_transactions(event: APIGatewayEvent, context: Context):
    chain = None

    if (ev := event.get("pathParameters")) is not None:
        chain = ev.get("chain")

    if not (chain := to_chain(chain)):
        return Response.make_bad_request(f"`chain` is invalid")

    if (ev := event.get("queryStringParameters")) is not None:
        from_address = try_hexbytes(ev.get("from", None))
        to_address = try_hexbytes(ev.get("to", None))
        page = int(ev.get("page", 0))

        if from_address is None and to_address is None:
            return Response.make_bad_request("`from` and `to` is null")

        return Response.make_response(
            exec_paginate_query(
                *txs_to_address(
                    chain,
                    from_address,
                    to_address,
                ),
                page=page,
            ),
        )

    return Response.make_bad_request("`chain`, `from` and `to` is null")
