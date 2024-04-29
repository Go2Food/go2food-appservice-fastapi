from pydantic import BaseModel

class Account(BaseModel):
    email: str
    username: str
    password: str
