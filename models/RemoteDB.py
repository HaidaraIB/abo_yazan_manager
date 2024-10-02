import mysql.connector
import mysql.connector.abstracts
from mysql.connector.errors import OperationalError, DatabaseError
import os
import sys


class MySqlConnSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:

            cls._instance = mysql.connector.connect(
                host=os.getenv("REMOTE_DB_HOST"),
                user=os.getenv("REMOTE_DB_USERNAME"),
                password=os.getenv("REMOTE_DB_PASSWORD"),
                database=os.getenv("REMOTE_DB_NAME"),
            )
        return cls._instance


def connect_to_remote(func):
    def wrapper(*args, **kwargs):
        try:
            db = MySqlConnSingleton()
            cr = db.cursor(dictionary=True)
        except (OperationalError, DatabaseError):
            os.execl(sys.executable, sys.executable, *sys.argv)
        result = func(*args, **kwargs, cr=cr)
        db.commit()
        return result

    return wrapper


class RemoteDB:
    @staticmethod
    @connect_to_remote
    def insert_into_remote_db(
        data: list,
        is_closed: int,
        cr: mysql.connector.abstracts.MySQLCursorAbstract = None,
    ):
        cr.execute(
            f"""
            INSERT INTO transactions (
                `trader-id`,
                `country`,
                `registery-date`,
                `balance`,
                `deposits-count`,
                `deposits-sum`,
                `withdrawals-count`,
                `withdrawals-sum`,
                `turnover-clear`,
                `vol-share`,
                `is-closed`
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (*data, is_closed),
        )

    @staticmethod
    @connect_to_remote
    def update_into_remote_db(
        data: list,
        is_closed: int,
        cr: mysql.connector.abstracts.MySQLCursorAbstract = None,
    ):
        cr.execute(
            f"""
                UPDATE transactions SET
                    `balance` = %s,
                    `deposits-count` = %s,
                    `deposits-sum` = %s,
                    `withdrawals-count` = %s,
                    `withdrawals-sum` = %s,
                    `turnover-clear` = %s,
                    `vol-share` = %s,
                    `is-closed` = %s
                WHERE `trader-id` = %s;
            """,
            (*data[3:], is_closed, data[0]),
        )

    @staticmethod
    @connect_to_remote
    def get_from_remote_db(
        trader_id: int, cr: mysql.connector.abstracts.MySQLCursorAbstract = None
    ):
        cr.execute(
            f"""
                SELECT * FROM transactions
                WHERE `trader-id` = %s;
            """,
            (trader_id,),
        )

        return cr.fetchone()
