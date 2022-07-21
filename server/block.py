#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.helpers.types import APIGatewayEvent, Context, to_chain
from lib.queries.blocks import closest_timestamp_to_block
from lib.helpers.postgres import exec_psql_query
from lib.helpers.serializer import Response


def block_closest_timestamp(event: APIGatewayEvent, context: Context):
    timestamp = None
    chain = None

    if (ev := event.get("pathParameters")) is not None:
        timestamp = int(ev.get("timestamp", 0))
        chain = ev.get("chain")

    if not (chain := to_chain(chain)):
        return Response.make_bad_request(f"`chain` is invalid")
    elif timestamp is None:
        return Response.make_bad_request(f"`timestamp` is null")

    return Response.make_response(
        exec_psql_query(
            *closest_timestamp_to_block(
                chain,
                timestamp,
            ),
        ),
    )
