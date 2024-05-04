from pydantic import BaseModel

class Menu(BaseModel):
    restaurant: str
    name: str
    pictureURL: str
    picture_name: str
    description: str
    category: str
    price: float