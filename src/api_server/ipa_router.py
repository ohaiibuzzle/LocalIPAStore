from fastapi.routing import APIRouter
from ipatool_comm.models import IPAToolAppSearch
from threading import Thread
import ipatool_comm


ipa_router = APIRouter()


@ipa_router.get("/ipa/search")
def _search_ipa(query: str) -> IPAToolAppSearch:
    """Search for an app in the App Store"""
    return ipatool_comm.search_ipa(query)


@ipa_router.post("/ipa/download")
def _download_ipa(bundle_id: str) -> dict:
    """Download an IPA from the App Store"""
    Thread(target=ipatool_comm.download_ipa, args=(bundle_id,)).start()
    return {"has_downloaded": True}


@ipa_router.post("/ipa/delete")
def _delete_ipa(bundle_id: str) -> dict:
    """Delete decrypted IPA"""
    return {"has_deleted": ipatool_comm.delete_ipa(bundle_id)}


@ipa_router.post("/ipa/delete_decrypted")
def _delete_decrypted_ipa(bundle_id: str) -> dict:
    """Delete decrypted IPA"""
    return {"has_deleted": ipatool_comm.delete_decrypted_ipa(bundle_id)}
