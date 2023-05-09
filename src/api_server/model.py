import pydantic


class PlayCoverIPALibraryFormat(pydantic.BaseModel):
    bundleID: str
    name: str
    version: str
    itunesLookup: str
    link: str
