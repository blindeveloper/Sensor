from pydantic import BaseModel


class RawClimateItem(BaseModel):
    name: str
    range: dict
    rows: list
    ts: str
    pt: int


class PathItem(BaseModel):
    month: str
    day: str
