from pydantic import BaseModel


class NewSessionDTO(BaseModel):
    postal_code: str
    food: str
    departure_time: str
    username: str


class SessionCodeDTO(BaseModel):
    session_code: str
    username: str
