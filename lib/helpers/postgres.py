#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from typing import Generator
import os

from psycopg.abc import Params, Query
from psycopg.rows import class_row
from psycopg.cursor import Cursor
import psycopg_pool

PSQL_CONN = psycopg_pool.ConnectionPool(os.environ["PSQL_URL"])


@contextmanager
def get_psql_conn(**cursor_args) -> Generator[Cursor, None, None]:
    """
    Creates a PostgreSQL database connection.
    Yields:
        Generator[Connection, None, None]: A context generator for the connection.
    Examples:
        >>> with get_psql_conn() as c:
        >>>     c.execute(...)
    """

    with PSQL_CONN.connection() as conn:
        # conn.autocommit = True
        yield conn.cursor(**cursor_args)


def exec_psql_query(sql: Query, params: Params, class_row_type):
    with get_psql_conn(row_factory=class_row(class_row_type)) as c:
        return c.execute(sql, params).fetchall()

    # Why would it ever reach here? Are you retarded mypy?
    return []
