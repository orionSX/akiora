from pydantic import BaseModel


class EmailRequest(BaseModel):
    email: str


class VerifyRequest(BaseModel):
    token: str
    code: str
