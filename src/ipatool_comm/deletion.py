from constants.directories import IPA_DIR, DECRYPTED_IPA_DIR
from .database import (
    _remove_ipa_from_library,
    _remove_ipa_from_decrypted_library,
)

import os


def delete_ipa(bundle_id: str) -> bool:
    """Delete decrypted IPA"""
    try:
        os.remove(f"{IPA_DIR}/{bundle_id}.ipa")
        _remove_ipa_from_library(bundle_id)
        return True
    except FileNotFoundError:
        return False


def delete_decrypted_ipa(bundle_id: str) -> bool:
    """Delete decrypted IPA"""
    try:
        os.remove(f"{DECRYPTED_IPA_DIR}/{bundle_id}.ipa")
        _remove_ipa_from_decrypted_library(bundle_id)
        return True
    except FileNotFoundError:
        return False
