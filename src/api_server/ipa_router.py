from fastapi.routing import APIRouter
from ipatool_comm.models import IPAToolAppSearch
import ipatool_comm

_ipa_router = APIRouter()


@_ipa_router.get("/ipa/search")
def _search_ipa(query: str) -> IPAToolAppSearch:
    """Search for an app in the App Store"""
    return ipatool_comm.search_ipa(query)


@_ipa_router.get("/ipa/download")
def _download_ipa(bundle_id: str) -> str:
    """Download an IPA from the App Store"""
    return ipatool_comm.download_ipa(bundle_id)
