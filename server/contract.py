#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.helpers.types import APIGatewayEvent, Context, to_chain
from lib.helpers.paginate import exec_paginate_query
from lib.queries.logs import logs_to_contract_address
from lib.helpers.hexbytes import try_hexbytes
from lib.helpers.serializer import Response


def contract_address_logs(event: APIGatewayEvent, context: Context):
    contract_address = None
    chain = None
    page = 0

    if (ev := event.get("pathParameters")) is not None:
        contract_address = try_hexbytes(ev.get("contract_address"))
        chain = ev.get("chain")

    if not (chain := to_chain(chain)):
        return Response.make_bad_request(f"`chain` is invalid")
    elif contract_address is None:
        return Response.make_bad_request("`contract_address` is null")

    if (ev := event.get("queryStringParameters")) is not None:
        topic0 = try_hexbytes(ev.get("topic0"))
        txhash = try_hexbytes(ev.get("txhash"))
        page = int(ev.get("page", 0))

        return Response.make_response(
            exec_paginate_query(
                *logs_to_contract_address(
                    chain,
                    contract_address,
                    topic0,
                    txhash,
                ),
                page=page,
            )
        )

    return Response.make_response(
        exec_paginate_query(
            *logs_to_contract_address(
                chain,
                contract_address,
                None,
                None,
            ),
            page=page,
        )
    )
