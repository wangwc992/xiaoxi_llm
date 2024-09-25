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


a = AAA(w="w")
z1 = a.model_dump()
z2 = a.dict()
z3 = a.model_dump_json(exclude_none=True)
z4 = a.dict()
z5 = AAA.model_validate_json(z3)
z6 = AAA.model_validate(z2)
print(z1)
# z1 变成字典类型

