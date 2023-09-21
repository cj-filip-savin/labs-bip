#
# Copyright (c) 2023 CUJO LLC
#
"""
This module contains database related functions.
"""
import sqlite3
import os
import logging

DB_FILE = os.path.realpath("data/db.sqlite")

logger = logging.getLogger(__name__)
logger.info("Using database %s", DB_FILE)


def connect(read_only=True):
    """Returns database connection handle."""
    mode = "ro" if read_only else "rw"
    return sqlite3.connect(f"file:{DB_FILE}?mode={mode}", uri=True)


def execute(sql, params=None, commit=False):
    """Executes specified SQL with parameters."""
    con = connect(not commit)
    cur = con.cursor()
    cur.execute(sql, params)
    if commit:
        con.commit()
    return cur
