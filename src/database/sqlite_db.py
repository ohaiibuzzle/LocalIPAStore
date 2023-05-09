from constants.directories import DATABASE_PATH
import sqlite3


class SqliteSingleton:
    __instance = None

    @staticmethod
    def getInstance():
        """Static access method."""
        if SqliteSingleton.__instance is None:
            SqliteSingleton()
        return SqliteSingleton.__instance

    def __init__(self):
        """Virtually private constructor."""
        if SqliteSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SqliteSingleton.__instance = self
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
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
