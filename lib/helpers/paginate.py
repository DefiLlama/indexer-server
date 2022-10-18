#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from psycopg.sql import SQL, Composed

from lib.helpers.postgres import exec_psql_query


def exec_paginate_query(
    sql: Composed, params: List, class_row_type, /, page: int = 0, limit: int = 500
):
    sql += SQL(" LIMIT {} OFFSET {}").format(limit, page * limit)

    # limit = 100
    # p0 0-99
    # p1 100-199
    # p2 200-299

    ret = exec_psql_query(
        sql,
        params,
        class_row_type,
    )

    return {
        "data": ret,
        "pagination": {
            # This is magic
            "has_more_pages": len(ret) == limit,
            "page_size": len(ret),
            "page": page,
        },
    }
