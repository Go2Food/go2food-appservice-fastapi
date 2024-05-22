from pydantic import BaseModel

class Account(BaseModel):
    email: str
    username: str
    password: str
    premium: bool
    balance: float
    location: str