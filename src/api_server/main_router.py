from fastapi.routing import APIRouter
from fastapi.responses import RedirectResponse
from .decrypt_router import decrypt_router
from .library_router import library_router
from .ipa_router import ipa_router
from .status_router import status_router

api_router = APIRouter()

api_router.include_router(decrypt_router)
api_router.include_router(library_router)
api_router.include_router(ipa_router)
api_router.include_router(status_router)


# redirect / and /ui to /ui/index.html
@api_router.get("/")
@api_router.get("/ui")
def _redirect_to_ui():
    return RedirectResponse(url="/ui/index.html")
