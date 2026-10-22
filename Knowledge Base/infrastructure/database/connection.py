
import os

from contextlib import contextmanager
from dotenv import load_dotenv
import pymysql

from pymysql.cursors import DictCursor


class DatabaseManager:

    def __init__(self):
        load_dotenv()

        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

        if not all([self.user, self.password, self.database]):
            raise ValueError(
                "Missing database configuration. "
                "Check your .env file."
            )

    def connect(self):
        """
        Establish and return a new MySQL connection.
        """

        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
            connect_timeout=10
        )

    @contextmanager
    def connection(self):
        """
        Provide a connection and close it afterward.

        Intended for operations that do not require
        an explicit transaction commit.
        """

        conn = self.connect()

        try:
            yield conn

        finally:
            conn.close()

    @contextmanager
    def transaction(self):
        """
        Execute database operations atomically.

        Commit on success.
        Roll back on failure.
        Always close the connection.
        """

        conn = self.connect()

        try:
            yield conn
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()