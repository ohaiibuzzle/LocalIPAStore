from constants.directories import DATABASE_PATH
import sqlite3


class SqliteSingleton:
    __instance = None

    @staticmethod
    def getInstance():
        """Static access method."""
        if SqliteSingleton.__instance is None:
            SqliteSingleton()
        if SqliteSingleton.__instance is not None:
            return SqliteSingleton.__instance
        else:
            raise Exception("Failed to initialize SQLite")

    def __init__(self):
        """Virtually private constructor."""
        if SqliteSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SqliteSingleton.__instance = self
            self.connection = sqlite3.connect(
                DATABASE_PATH, check_same_thread=False
            )
            self.cursor = self.connection.cursor()

    def __enter__(self):
        return self.getInstance()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params) if params else self.cursor.execute(
            query
        )
        self.connection.commit()
        return self.cursor

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()
