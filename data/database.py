from mariadb import connect
from mariadb.connections import Connection
from os import environ
from dotenv import load_dotenv

load_dotenv()

def _get_connection() -> Connection:
    return connect(
        user=environ["DB_USER"],
        password=environ["DB_PASSWORD"],
        host=environ.get("DB_HOST", "localhost"),
        port=int(environ.get("DB_PORT", "3306")),
        database=environ["DB_NAME"],
    )


def read_query(sql: str, sql_params=()) -> list[tuple]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.rowcount
