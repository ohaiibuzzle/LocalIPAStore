from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .model import StatusResponse, DecryptionRequest
from frida_comm import run_ipa_decrypt
from threading import Thread

decrypt_router = APIRouter()


@decrypt_router.post("/decrypt")
def _decrypt_ipa(
    data: DecryptionRequest,
) -> JSONResponse:
    try:
        # spawn a new thread to run the decryption

        Thread(
            target=run_ipa_decrypt,
            args=(
                data.bundle_id,
                data.blacklist,
                data.ssh_params,
            )
            if data.ssh_params
            else (data.bundle_id, data.blacklist),
        ).start()
        return JSONResponse(
            status_code=200,
            content=StatusResponse(
                status="success",
                message="Successfully started decrypting the IPA",
            ).dict(),
        )

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=StatusResponse(
                status="failure",
                message="An error occurred while decrypting the IPA",
                error=str(e),
            ).dict(),
        )
