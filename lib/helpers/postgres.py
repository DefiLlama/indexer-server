#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Generator, List, Type, TypeVar
from contextlib import contextmanager
import os

from psycopg.abc import Params, Query
from psycopg.rows import class_row
from psycopg.cursor import Cursor
import psycopg_pool

PSQL_CONN = psycopg_pool.ConnectionPool(os.environ["PSQL_URL"])
T = TypeVar("T")


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


def exec_psql_query(
    sql: Query, params: Params, class_row_type: Type[T] = None
) -> List[T]:
    rf = None
    if class_row_type is not None:
        rf = class_row(class_row_type)

    with get_psql_conn(row_factory=rf) as c:
        return c.execute(sql, params).fetchall()
