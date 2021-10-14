from pydantic import BaseModel


class LoginBodyDTO(BaseModel):
    email: str


class RateUserDTO(BaseModel):
    username: str
    rating: float
    dabaoer: str
    session_code: str
