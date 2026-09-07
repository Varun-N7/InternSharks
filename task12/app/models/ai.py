from pydantic import BaseModel


class AIGenerateRequest(BaseModel):

    prompt: str
