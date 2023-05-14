# flake8: noqa
# pyright: reportUnboundVariable=false, reportGeneralTypeIssues=false
# Author : AloneMonkey
# blog: www.alonemonkey.com

from __future__ import print_function
from __future__ import unicode_literals
import sys
import codecs
import frida
import threading
import os
import shutil
import tempfile
import subprocess
import re
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from tqdm import tqdm
import traceback
from .ssh_connection import SSHConnection
from database import SqliteSingleton
from ipatool_comm import download_ipa
from constants.directories import IPA_DIR, DECRYPTED_IPA_DIR
from libimobiledevice_comm import install_ipa, uninstall_ipa
from api_server.status_router import TASKS

script_dir = os.path.dirname(os.path.realpath(__file__))

DUMP_JS = os.path.join(script_dir, "dump.js")

TEMP_DIR = tempfile.gettempdir()
PAYLOAD_DIR = "Payload"
PAYLOAD_PATH = os.path.join(TEMP_DIR, PAYLOAD_DIR)
file_dict = {}

finished = threading.Event()

SSH_SESSION = None


def _get_usb_iphone() -> frida.core.Device:
    Type = "usb"
    if int(frida.__version__.split(".")[0]) < 12:
        Type = "tether"
    device_manager = frida.get_device_manager()
    changed = threading.Event()

    def on_changed():
        changed.set()

    device_manager.on("changed", on_changed)

    device = None
    while device is None:
        devices = [
            dev
            for dev in device_manager.enumerate_devices()
            if dev.type == Type
        ]
        if len(devices) == 0:
            print("Waiting for USB device...")
            changed.wait()
        else:
            device = devices[0]

    device_manager.off("changed", on_changed)

    return device


def _generate_ipa(path, display_name):
    ipa_filename = display_name + ".ipa"

    print('Generating "{}"'.format(ipa_filename))
    try:
        app_name = file_dict["app"]

        for key, value in file_dict.items():
            from_dir = os.path.join(path, key)
            to_dir = os.path.join(path, app_name, value)
            if key != "app":
                shutil.move(from_dir, to_dir)

        target_dir = TEMP_DIR + "/" + PAYLOAD_DIR
        # zip_args = (
        #     "zip",
        #     "-r",
        #     os.path.join(os.getcwd(), ipa_filename),
        #     target_dir,
        # )
        # subprocess.check_call(zip_args, cwd=TEMP_DIR)
        # Zipping into IPA, including the Payload folder
        shutil.make_archive(
            os.path.join(os.getcwd(), ipa_filename),
            "zip",
            target_dir + "/..",
            "Payload",
        )

        # remove `zip` from the end of the filename
        os.rename(
            os.path.join(os.getcwd(), ipa_filename + ".zip"),
            os.path.join(os.getcwd(), ipa_filename),
        )
        shutil.rmtree(PAYLOAD_PATH)
        finished.set()
    except Exception as e:
        print(e)
        finished.set()


def _on_message(message, data):
    global SSH_SESSION

    # print(f"Script Message: {message}")

    if message["type"] == "error":
        # finished.set()
        raise Exception(message["stack"])

    if "payload" in message:
        payload = message["payload"]
        if "dump" in payload:
            origin_path = payload["path"]
            dump_path = payload["dump"]

            scp_from = dump_path
            scp_to = PAYLOAD_PATH + "/"

            with SCPClient(
                SSH_SESSION.get_transport(), socket_timeout=60
            ) as scp:
                scp.get(scp_from, scp_to)

            chmod_dir = os.path.join(PAYLOAD_PATH, os.path.basename(dump_path))
            chmod_args = ("chmod", "655", chmod_dir)
            try:
                subprocess.check_call(chmod_args)
            except subprocess.CalledProcessError as err:
                print(err)

            index = origin_path.find(".app/")
            file_dict[os.path.basename(dump_path)] = origin_path[index + 5 :]

        if "app" in payload:
            app_path = payload["app"]

            scp_from = app_path
            scp_to = PAYLOAD_PATH + "/"
            with SCPClient(
                SSH_SESSION.get_transport(), socket_timeout=60
            ) as scp:
                scp.get(scp_from, scp_to, recursive=True)

            chmod_dir = os.path.join(PAYLOAD_PATH, os.path.basename(app_path))
            chmod_args = ("chmod", "755", chmod_dir)
            try:
                subprocess.check_call(chmod_args)
            except subprocess.CalledProcessError as err:
                print(err)

            file_dict["app"] = os.path.basename(app_path)

        if "done" in payload:
            finished.set()


def _compare_applications(a, b):
    a_is_running = a.pid != 0
    b_is_running = b.pid != 0
    if a_is_running == b_is_running:
        if a.name > b.name:
            return 1
        elif a.name < b.name:
            return -1
        else:
            return 0
    elif a_is_running:
        return -1
    else:
        return 1


def _cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""

    class K:
        def __init__(self, obj):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


def _get_applications(device):
    try:
        applications = device.enumerate_applications()
    except Exception as e:
        sys.exit("Failed to enumerate applications: %s" % e)

    return applications


def _list_applications(device):
    applications = _get_applications(device)

    if len(applications) > 0:
        pid_column_width = max(
            map(lambda app: len("{}".format(app.pid)), applications)
        )
        name_column_width = max(map(lambda app: len(app.name), applications))
        identifier_column_width = max(
            map(lambda app: len(app.identifier), applications)
        )
    else:
        pid_column_width = 0
        name_column_width = 0
        identifier_column_width = 0

    header_format = (
        "%"
        + str(pid_column_width)
        + "s  "
        + "%-"
        + str(name_column_width)
        + "s  "
        + "%-"
        + str(identifier_column_width)
        + "s"
    )
    print(header_format % ("PID", "Name", "Identifier"))
    print(
        "%s  %s  %s"
        % (
            pid_column_width * "-",
            name_column_width * "-",
            identifier_column_width * "-",
        )
    )
    line_format = (
        "%"
        + str(pid_column_width)
        + "s  "
        + "%-"
        + str(name_column_width)
        + "s  "
        + "%-"
        + str(identifier_column_width)
        + "s"
    )
    for application in sorted(
        applications, key=_cmp_to_key(_compare_applications)
    ):
        if application.pid == 0:
            print(
                line_format % ("-", application.name, application.identifier)
            )
        else:
            print(
                line_format
                % (application.pid, application.name, application.identifier)
            )


def _load_js_file(session, filename):
    source = ""
    with codecs.open(filename, "r", "utf-8") as f:
        source = source + f.read()
    script = session.create_script(source)
    script.on("message", _on_message)
    script.load()

    return script


def _create_dir(path):
    path = path.strip()
    path = path.rstrip("\\")
    if os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.makedirs(path)
    except os.error as err:
        print(err)


def _open_target_app(device: frida.core.Device, name_or_bundleid: str):
    print("Start the target app {}".format(name_or_bundleid))

    pid = ""
    session = None
    display_name = ""
    bundle_identifier = ""
    for application in _get_applications(device):
        if (
            name_or_bundleid == application.identifier
            or name_or_bundleid == application.name
        ):
            pid = application.pid
            display_name = application.name
            bundle_identifier = application.identifier

    try:
        if not pid:
            pid = device.spawn([bundle_identifier])
            session = device.attach(pid)
            device.resume(pid)
        else:
            session = device.attach(pid)
    except Exception as e:
        print(e)

    return session, display_name, bundle_identifier


def _start_dump(session, ipa_name, bundle_identifier, blacklisted_dirs=[]):
    # Freeze the app
    print("Dumping {} to {}".format(bundle_identifier, TEMP_DIR))

    script = _load_js_file(session, DUMP_JS)
    script.post({"action": "dump", "blacklist": blacklisted_dirs})
    finished.wait()

    print("Dumping {} to {} finished".format(bundle_identifier, TEMP_DIR))
    _generate_ipa(PAYLOAD_PATH, ipa_name)

    if session:
        session.detach()


def _run_ipa_decrypt(
    target: str,
    output_ipa: str,
    blacklisted_dirs: list[str] = [],
    ssh_params: SSHConnection = SSHConnection(),
):
    global SSH_SESSION

    device = _get_usb_iphone()

    name_or_bundleid = target
    output_ipa = output_ipa
    # update ssh args
    Host = ssh_params.host
    Port = int(ssh_params.port)
    User = ssh_params.username
    Password = ssh_params.password
    KeyFileName = ssh_params.key_file_name

    try:
        SSH_SESSION = paramiko.SSHClient()
        SSH_SESSION.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SSH_SESSION.connect(
            Host,
            port=Port,
            username=User,
            password=Password,
            key_filename=KeyFileName if KeyFileName else None,
        )

        _create_dir(PAYLOAD_PATH)

        (session, display_name, bundle_identifier) = _open_target_app(
            device, name_or_bundleid
        )

        if output_ipa is None:
            output_ipa = display_name
        output_ipa = re.sub(".ipa$", "", output_ipa)
        if session:
            _start_dump(
                session, output_ipa, bundle_identifier, blacklisted_dirs
            )
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(e)
        print("Try specifying -H/--hostname and/or -p/--port")
    except paramiko.AuthenticationException as e:
        print(e)
        print("Try specifying -u/--username and/or -P/--password")
    except Exception as e:
        print("*** Caught exception: %s: %s" % (e.__class__, e))
        traceback.print_exc()

    if SSH_SESSION:
        SSH_SESSION.close()

    if os.path.exists(PAYLOAD_PATH):
        shutil.rmtree(PAYLOAD_PATH)


# ipa_table_query = """
# CREATE TABLE IF NOT EXISTS IPALibrary (
#     id INTEGER PRIMARY KEY,
#     bundle_id TEXT NOT NULL,
#     name TEXT NOT NULL,
#     version TEXT NOT NULL,
#     ipa_path TEXT NOT NULL
#     );
# """
# decrypted_ipa_table_query = """
# CREATE TABLE IF NOT EXISTS DecryptedIPALibrary (
#     id INTEGER PRIMARY KEY,
#     bundle_id TEXT NOT NULL,
#     name TEXT NOT NULL,
#     version TEXT NOT NULL,
#     decrypted_ipa_path TEXT NOT NULL
#     );
# """


def run_ipa_decrypt(
    bundle_id: str,
    blacklisted_dirs: list[str] = [],
    ssh_params: SSHConnection = SSHConnection(),
):
    TASKS.append("Decrypting {}".format(bundle_id))

    q1 = """
    SELECT * FROM IPALibrary WHERE bundle_id = ?;
    """
    query1 = SqliteSingleton.getInstance().execute(q1, (bundle_id,))
    result = query1.fetchone()
    if result is None:
        download_ipa(bundle_id)
        target = f"{IPA_DIR}/{bundle_id}.ipa"
    else:
        target = result[4]

    # refresh query
    query1 = SqliteSingleton.getInstance().execute(q1, (bundle_id,))
    result = query1.fetchone()

    output_ipa = f"{DECRYPTED_IPA_DIR}/{bundle_id}.ipa"

    install_ipa(target)
    _run_ipa_decrypt(bundle_id, output_ipa, blacklisted_dirs, ssh_params)
    uninstall_ipa(bundle_id)

    q2 = """
    INSERT INTO DecryptedIPALibrary (id, bundle_id, name, version, decrypted_ipa_path)
    VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET bundle_id = ?, name = ?, version = ?, decrypted_ipa_path = ?;
    """
    SqliteSingleton.getInstance().execute(
        q2,
        (
            result[0],
            result[1],
            result[2],
            result[3],
            output_ipa,
            result[1],
            result[2],
            result[3],
            output_ipa,
        ),
    )

    TASKS.remove("Decrypting {}".format(bundle_id))
