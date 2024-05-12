from pydantic import BaseModel

class RestaurantAccount(BaseModel):
    email: str
    password: str
    restaurant: str
