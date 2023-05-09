# Bootstrap for LocalIPAStore

import os
import urllib.request
import json
import platform
import hashlib
from constants.directories import TOOLS_DIR


def _get_ipatool():
    """Return the version of the ipatool binary."""
    if os.path.exists(TOOLS_DIR):
        with open(TOOLS_DIR + "/ipatool.version", "r") as f:
            return f.read().strip()


def _update_ipatool():
    """Update the ipatool binary."""

    # First check the GitHub API to see if there is a new version
    # https://github.com/majd/ipatool
    # https://api.github.com/repos/majd/ipatool/releases/latest
    upd_request = urllib.request.urlopen(
        "https://api.github.com/repos/majd/ipatool/releases/latest"
    )
    upd_data = upd_request.read()
    upd_request.close()
    upd_json = json.loads(upd_data)
    latest_release = upd_json["tag_name"]

    if latest_release != _get_ipatool():
        # Download the latest version
        # Downloads follows ipatool-2.0.3-linux-amd64.tar.gz
        latest_release = latest_release[1:]

        sys_os = platform.system().lower()
        sys_arch = platform.machine().lower()
        if sys_os == "darwin":
            sys_os = "macos"

        if sys_arch == "x86_64":
            sys_arch = "amd64"

        download = urllib.request.urlopen(
            "https://github.com/majd/ipatool/releases/download"
            f"/v{latest_release}/"
            f"ipatool-{latest_release}"
            f"-{sys_os}"
            f"-{sys_arch}.tar.gz"
        )
        download_data = download.read()
        download.close()

        shasum = urllib.request.urlopen(
            "https://github.com/majd/ipatool/releases/download"
            f"/v{latest_release}/"
            f"/ipatool-{latest_release}"
            f"-{sys_os}"
            f"-{sys_arch}.tar.gz.sha256sum"
        )
        shasum_data = shasum.read()
        shasum.close()

        # Check the SHA256 sum
        if (
            shasum_data.split()[0].decode("utf-8")
            != hashlib.sha256(download_data).hexdigest()
        ):
            raise Exception("SHA256 sum mismatch")

        # Extract the archive
        import tarfile
        import io

        ipatool_tar = tarfile.open(fileobj=io.BytesIO(download_data))
        # Put the content of the bin subdirectory
        ipatool_tar.extractall(
            TOOLS_DIR,
            members=[
                member
                for member in ipatool_tar.getmembers()
                if member.name.startswith("bin")
            ],
        )
        ipatool_tar.close()
        # Move the ipatool binary to the root of the tools directory
        os.rename(
            TOOLS_DIR + f"/bin/ipatool-{latest_release}-{sys_os}-{sys_arch}",
            TOOLS_DIR + "/ipatool",
        )
        # Remove the bin directory
        os.rmdir(TOOLS_DIR + "/bin")
        # Set the executable bit
        os.chmod(TOOLS_DIR + "/ipatool", 0o755)

        # Write the version to a file
        with open(TOOLS_DIR + "/ipatool.version", "w") as f:
            f.write(latest_release)
    else:
        return
    pass


def _check_libimobiledevice():
    """Check if libimobiledevice is installed."""
    # This thing is way too platform-agnostic to be automatically downloaded
    # We'll just check if it's installed by checking if ideviceinfo exists

    import shutil

    if shutil.which("ideviceinfo") is None:
        raise Exception("libimobiledevice is not installed")
    pass


def _check_ideviceinstaller():
    """Check if ideviceinstaller is installed."""
    # This thing is way too platform-agnostic to be automatically downloaded
    # We'll just check if it's installed by checking if ideviceinstaller exists

    import shutil

    if shutil.which("ideviceinstaller") is None:
        raise Exception("ideviceinstaller is not installed")
    pass


def check_tools():
    """Check if the tools are installed."""
    _check_libimobiledevice()
    _check_ideviceinstaller()
    _update_ipatool()

    return True
