import bootstrap
import ipatool_comm


def checks():
    bootstrap.check_tools()
    bootstrap.check_authentication()
    bootstrap.bootstrap_database()
    bootstrap.bootstrap_directories()


def start_fastapi_server():
    # TODO: Add FastAPI server
    pass


def main():
    checks()
    start_fastapi_server()
    ipatool_comm.download_ipa("net.openvpn.connect.app")


if __name__ == "__main__":
    main()
