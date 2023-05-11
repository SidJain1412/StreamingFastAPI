from pydantic import BaseModel, Field
import config


class OverloadError(BaseModel):
    detail: str = Field(default=config.error503)


class ProfanityError(BaseModel):
    detail: str = Field(default=config.profanityError)
