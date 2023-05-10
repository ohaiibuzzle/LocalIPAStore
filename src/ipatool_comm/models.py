import pydantic


class IPAToolAppInfo(pydantic.BaseModel):
    id: str
    bundleID: str
    name: str
    price: str
    version: str


class IPAToolAppSearch(pydantic.BaseModel):
    apps: list[IPAToolAppInfo]
