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
