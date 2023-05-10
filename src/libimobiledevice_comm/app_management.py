import subprocess
from .semaphore import InstallSemaphore


def install_ipa(path: str) -> bool:
    """Install an IPA to the device"""
    InstallSemaphore.acquire()
    run = subprocess.run(
        [
            "ideviceinstaller",
            "-i",
            path,
        ]
    )
    InstallSemaphore.release()
    if run.returncode == 0:
        return True
    else:
        raise Exception(f"Failed to install IPA: {run.stderr.decode()}")


def uninstall_ipa(bundle_id: str) -> bool:
    """Uninstall an IPA from the device"""
    InstallSemaphore.acquire()
    run = subprocess.run(
        [
            "ideviceinstaller",
            "-U",
            bundle_id,
        ]
    )
    InstallSemaphore.release()
    if run.returncode == 0:
        return True
    else:
        raise Exception(f"Failed to uninstall IPA: {run.stderr.decode()}")
