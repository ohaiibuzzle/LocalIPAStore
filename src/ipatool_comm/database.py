from database import SqliteSingleton


def _add_ipa_to_library(bundle_id, name, version, ipa_path):
    """Add an IPA to the database"""
    query = """
    INSERT INTO IPALibrary (bundle_id, name, version, ipa_path)
    VALUES (?, ?, ?, ?);
    """
    SqliteSingleton().execute(query, (bundle_id, name, version, ipa_path))
