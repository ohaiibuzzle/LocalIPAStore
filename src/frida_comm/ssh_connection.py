from pydantic import BaseModel


class SSHConnection(BaseModel):
    host: str = "localhost"
    port: int = 2222
    username: str = "root"
    password: str = "alpine"
    key_file_name: str | None = None
