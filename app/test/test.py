from pydantic import BaseModel


class AiChatWeaviateModel(BaseModel):
    a :str


z = AiChatWeaviateModel(a="a")

print(z.dict())
print(z.__dict__)

