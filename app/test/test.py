from datetime import datetime

from pydantic import BaseModel

class s(BaseModel):
    times: datetime

x = s(times='2021-01-01 00:00:00')
print(x)


