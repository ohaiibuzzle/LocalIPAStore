from constants.directories import TOOLS_DIR, IPA_DIR
from .database import _add_ipa_to_library

import subprocess
import urllib.request
import json


def _get_itunes_info(bundle_id: str) -> dict:
    """Get iTunes info for an app"""
    with urllib.request.urlopen(
        f"https://itunes.apple.com/lookup?bundleId={bundle_id}&country=jp"
    ) as response:
        return json.loads(response.read())["results"][0]


def download_ipa(bundle_id: str) -> bool:
    """Download an IPA from the App Store"""

    run = subprocess.run(
        [
            f"{TOOLS_DIR}/ipatool",
            "download",
            "-b",
            bundle_id,
            "--purchase",
            "--output",
            f"{IPA_DIR}/{bundle_id}.ipa",
            "--format",
            "json",
        ]
    )
    if run.returncode == 0:
        itunes_lookup = _get_itunes_info(bundle_id)
        _add_ipa_to_library(
            itunes_lookup["trackId"],
            bundle_id,
            itunes_lookup["trackName"],
            itunes_lookup["version"],
            f"{IPA_DIR}/{bundle_id}.ipa",
        )

        return True
    else:
        raise Exception("Failed to download IPA")
