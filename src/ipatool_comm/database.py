from database import SqliteSingleton


def _add_ipa_to_library(id, bundle_id, name, version, ipa_path):
    """Add an IPA to the database"""
    query = """
    INSERT INTO IPALibrary (id, bundle_id, name, version, ipa_path)
    VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET
    id=?, bundle_id=?, name=?, version=?, ipa_path=?;
    """
    db = SqliteSingleton.getInstance()
    if db is not None:
        db.execute(
            query,
            (
                id,
                bundle_id,
                name,
                version,
                ipa_path,
                id,
                bundle_id,
                name,
                version,
                ipa_path,
            ),
        )


def _remove_ipa_from_decrypted_library(id):
    """Remove an IPA from the database"""
    query = """
    DELETE FROM DecryptedIPALibrary WHERE bundle_id=?;
    """
    db = SqliteSingleton.getInstance()
    if db is not None:
        db.execute(query, (id,))


def _remove_ipa_from_library(bundle_id):
    """Remove an IPA from the database"""
    query = """
    DELETE FROM IPALibrary WHERE bundle_id=?;
    """
    db = SqliteSingleton.getInstance()
    if db is not None:
        db.execute(query, (bundle_id,))
