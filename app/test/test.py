from typing import Optional

from pydantic import BaseModel, Field


class BBB(BaseModel):
    e: Optional[str] = None
    r: Optional[str] = None
    pass


class AAA(BaseModel):
    q: Optional[str] = "None"
    w: Optional[str]
    bbb: Optional[BBB] = Field(default_factory=BBB)


a = AAA(w = "w")
print(a.model_dump_json(exclude_unset=True))
print(a.model_dump_json(exclude_defaults=True))
print(a.model_dump_json(exclude_none=True))
