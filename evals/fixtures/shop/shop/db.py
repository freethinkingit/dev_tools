import sqlite3


def connect(path=":memory:"):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def query(connection, sql, params=()):
    return [dict(row) for row in connection.execute(sql, params)]
