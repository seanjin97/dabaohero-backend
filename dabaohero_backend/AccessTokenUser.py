from pydantic import BaseModel


class AccessUser(BaseModel):
    sub: str
