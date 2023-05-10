from constants.directories import DATABASE_PATH
from database.sqlite_db import SqliteSingleton
import os


def _initialize_database():
    ipa_table_query = """
    CREATE TABLE IF NOT EXISTS IPALibrary (
        id INTEGER PRIMARY KEY,
        bundle_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        ipa_path TEXT NOT NULL
        );
    """
    decrypted_ipa_table_query = """
    CREATE TABLE IF NOT EXISTS DecryptedIPALibrary (
        id INTEGER PRIMARY KEY,
        bundle_id TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        decrypted_ipa_path TEXT NOT NULL
        );
    """

    SqliteSingleton.getInstance().execute(ipa_table_query)
    SqliteSingleton.getInstance().execute(decrypted_ipa_table_query)


def bootstrap_database():
    """Check if the database exists and create it if it doesn't"""
    if not os.path.exists(DATABASE_PATH):
        _initialize_database()
