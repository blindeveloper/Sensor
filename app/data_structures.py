from pydantic import BaseModel, RootModel
from typing import List


class RawClimateItem(BaseModel):
    name: str
    range: dict
    rows: list
    ts: str
    pt: int


class RawClimateList(RootModel):
    List[RawClimateItem]


class PathItem(BaseModel):
    month: str
    day: str
