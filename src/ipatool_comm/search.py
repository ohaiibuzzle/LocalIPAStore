from constants.directories import TOOLS_DIR
import json
import subprocess

from .models import IPAToolAppSearch


def search_ipa(query: str) -> IPAToolAppSearch:
    """Search for an app in the App Store"""
    run = subprocess.run(
        [
            f"{TOOLS_DIR}/ipatool",
            "search",
            query,
            "--non-interactive",
            "--format",
            "json",
        ],
        capture_output=True,
    )
    if run.returncode == 0:
        return IPAToolAppSearch(**json.loads(run.stdout))
    else:
        return None
