import pydantic

from typing import Optional
from frida_comm.ssh_connection import SSHConnection


class PlayCoverIPALibraryFormat(pydantic.BaseModel):
    bundleID: str
    name: str
    version: str
    itunesLookup: str
    link: str


class StatusResponse(pydantic.BaseModel):
    status: str
    message: str | None = None
    error: str | None = None


class DecryptionRequest(pydantic.BaseModel):
    bundle_id: str
    blacklist: list[str] = []
    ssh_params: Optional[SSHConnection] = None
