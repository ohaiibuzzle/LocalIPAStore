from constants.directories import TOOLS_DIR

import subprocess


def _check_ipatool_authentication():
    """Check if ipatool is authenticated with Apple"""
    try:
        run = subprocess.run(
            [
                f"{TOOLS_DIR}/ipatool",
                "auth",
                "info",
            ]
        )
        if run.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def _authenticate_ipatool():
    """Authenticate ipatool with Apple"""
    # Exec ipatool auth login in interactive mode
    subprocess.run(
        [
            f"{TOOLS_DIR}/ipatool",
            "auth",
            "login",
        ]
    )


def check_authentication():
    """Check if ipatool is authenticated with Apple"""
    if not _check_ipatool_authentication():
        _authenticate_ipatool()
