import subprocess
from .semaphore import InstallSemaphore
from api_server.status_router import TASKS


def install_ipa(path: str) -> bool:
    """Install an IPA to the device"""
    TASKS.append(f"Installing {path}")

    InstallSemaphore.acquire()
    run = subprocess.run(
        [
            "ideviceinstaller",
            "-i",
            path,
        ]
    )
    InstallSemaphore.release()
    TASKS.remove(f"Installing {path}")
    if run.returncode == 0:
        return True
    else:
        raise Exception(f"Failed to install IPA: {run.stderr.decode()}")


def uninstall_ipa(bundle_id: str) -> bool:
    """Uninstall an IPA from the device"""
    TASKS.append(f"Uninstalling {bundle_id}")

    InstallSemaphore.acquire()
    run = subprocess.run(
        [
            "ideviceinstaller",
            "-U",
            bundle_id,
        ]
    )
    InstallSemaphore.release()
    TASKS.remove(f"Uninstalling {bundle_id}")

    if run.returncode == 0:
        return True
    else:
        raise Exception(f"Failed to uninstall IPA: {run.stderr.decode()}")
