from bson import ObjectId
from pydantic import BaseModel

class Restaurant(BaseModel):
    name: str
    pictureURL: str
    picture_name: str
    categories: list[str]
    menus: list[str]
    longitude: float
    latitude: float
    rating: float

