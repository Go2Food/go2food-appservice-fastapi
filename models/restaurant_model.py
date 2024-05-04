from pydantic import BaseModel

class Restaurant(BaseModel):
    name: str
    pictureURL: str
    picture_name: str
    categories: list[str]
    latitude: float
    longitude: float
    rating: float