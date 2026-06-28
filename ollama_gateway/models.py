from pydantic import BaseModel


class GenerateRequest(BaseModel):
    model: str
    prompt: str

class EmbedRequest(BaseModel):
    model: str
    text: str
