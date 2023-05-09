import subprocess
from .semaphore import InstallSemaphore


def _install_ipa(path: str) -> bool:
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
        return False


def _uninstall_ipa(bundle_id: str) -> bool:
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
        return False
