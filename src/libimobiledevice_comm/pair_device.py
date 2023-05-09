import subprocess


def _pair_device() -> bool:
    """Pair the device with the computer"""
    run = subprocess.run(
        [
            "idevicepair",
            "pair",
        ]
    )
    if run.returncode == 0:
        return True
    else:
        return False


def check_device_pair() -> bool:
    """Check if the device is paired with the computer"""
    run = subprocess.run(
        [
            "idevicepair",
            "-u",
            "auto",
            "validate",
        ]
    )
    if run.returncode == 0:
        return True
    else:
        return False
