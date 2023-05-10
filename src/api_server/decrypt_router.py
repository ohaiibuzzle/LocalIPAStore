from fastapi import APIRouter
from .model import StatusResponse, DecryptionRequest
from frida_comm import run_ipa_decrypt

decrypt_router = APIRouter()


@decrypt_router.post("/decrypt")
def _decrypt_ipa(
    data: DecryptionRequest,
) -> StatusResponse:
    try:
        run_ipa_decrypt(
            data.bundle_id, data.blacklist, data.ssh_params
        ) if data.ssh_params else run_ipa_decrypt(
            data.bundle_id, data.blacklist
        )
        return StatusResponse(status="success")
    except Exception as e:
        return StatusResponse(status="failure", message=str(e))
