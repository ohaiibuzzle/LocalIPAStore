from fastapi.routing import APIRouter
from .model import PlayCoverIPALibraryFormat
from database import SqliteSingleton

library_router = APIRouter()


@library_router.get("/library")
def _get_library() -> list[PlayCoverIPALibraryFormat]:
    data = SqliteSingleton().execute("SELECT * FROM IPALibrary")
    for row in data:
        yield PlayCoverIPALibraryFormat(
            bundle_id=row[1],
            name=row[2],
            version=row[3],
            itunesLookup=f"https://itunes.apple.com/lookup?bundleId={row[1]}",
            link=f"http://localhost:8000/ipa/download?bundle_id={row[1]}",
        )
