from pydantic import BaseModel
import datetime


class NewSessionDTO(BaseModel):
    postal_code: str
    food: str
    departure_time: datetime.datetime
    username: str


class SessionCodeDTO(BaseModel):
    session_code: str
    username: str
