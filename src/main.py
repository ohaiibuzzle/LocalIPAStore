import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import api_server
import bootstrap
from constants.directories import DECRYPTED_IPA_DIR

TEST_APP = "net.openvpn.connect.app"


def checks():
    bootstrap.check_tools()
    bootstrap.check_authentication()
    bootstrap.bootstrap_database()
    bootstrap.bootstrap_directories()


def start_fastapi_server():
    app = FastAPI()
    app.include_router(api_server.api_router)
    app.mount(
        "/decrypted_ipa",
        StaticFiles(directory=DECRYPTED_IPA_DIR),
        name="decrypted_ipa",
    )
    uvicorn.run(app, host="localhost", port=8000)
    pass


def main():
    checks()
    start_fastapi_server()


if __name__ == "__main__":
    main()
