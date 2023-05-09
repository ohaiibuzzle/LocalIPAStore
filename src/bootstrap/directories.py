import os
from constants.directories import WORK_DIR, TOOLS_DIR, IPA_DIR


def bootstrap_directories():
    # Create the directories within the constants
    for directory in [
        WORK_DIR,
        TOOLS_DIR,
        IPA_DIR,
    ]:
        os.makedirs(directory, exist_ok=True)
    # Create the directories within the runtime
