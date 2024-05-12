from pydantic import BaseModel

class NewAccount(BaseModel):
    email: str
    username: str
    password: str

class NewRestaurantAccount(BaseModel):
    email: str
    password: str

class NewAccountGoogle(BaseModel):
    email: str
    username: str

class PassCheck(BaseModel):
    email: str
    password: str

class ValidateToken(BaseModel):
    token: str

class GetById(BaseModel):
    id: str

class LocationForm(BaseModel):
    latitude: float
    longitude: float

class IdLocationForm(BaseModel):
    id: str
    latitude: float
    longitude: float