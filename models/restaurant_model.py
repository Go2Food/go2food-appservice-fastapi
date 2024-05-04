from pydantic import BaseModel

class Restaurant(BaseModel):
    name: str
    pictureURL: str
    picture_name: str
    categories: list[str]
    longitude: float
    latitude: float
    rating: float