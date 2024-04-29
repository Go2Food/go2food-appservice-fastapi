from pydantic import BaseModel

class NewAccount(BaseModel):
    email: str
    username: str
    password: str

class PassCheck(BaseModel):
    email: str
    password: str

class ValidateToken(BaseModel):
    token: str