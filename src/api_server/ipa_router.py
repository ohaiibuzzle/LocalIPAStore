from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from ipatool_comm.models import IPAToolAppSearch
import ipatool_comm
from constants.directories import DECRYPTED_IPA_DIR

ipa_router = APIRouter()


@ipa_router.post("/ipa/search")
def _search_ipa(query: str) -> IPAToolAppSearch:
    """Search for an app in the App Store"""
    return ipatool_comm.search_ipa(query)


@ipa_router.post("/ipa/download")
def _download_ipa(bundle_id: str) -> dict:
    """Download an IPA from the App Store"""
    return {"has_downloaded": ipatool_comm.download_ipa(bundle_id)}


ipa_router.mount(
    "/decrypted_ipa",
    StaticFiles(directory=DECRYPTED_IPA_DIR),
    name="decrypted_ipa",
)
