from pydantic import BaseModel, Field

error503 = "OpenAI server is busy, try again later"


class OverloadError(BaseModel):
    detail: str = Field(default=error503)
