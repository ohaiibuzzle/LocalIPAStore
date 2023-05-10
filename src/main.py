import bootstrap
import api_server
from fastapi import FastAPI
import uvicorn

TEST_APP = "net.openvpn.connect.app"


def checks():
    bootstrap.check_tools()
    bootstrap.check_authentication()
    bootstrap.bootstrap_database()
    bootstrap.bootstrap_directories()


def start_fastapi_server():
    app = FastAPI()
    app.include_router(api_server.api_router)
    uvicorn.run(app, host="localhost", port=8000)
    pass


def main():
    checks()
    start_fastapi_server()


if __name__ == "__main__":
    main()
