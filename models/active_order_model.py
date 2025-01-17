from pydantic import BaseModel
from datetime import datetime

class Item(BaseModel):
    item_id: str
    name: str
    amount: int
    price: float

class ActiveOrder(BaseModel):
    user_id: str
    username: str
    restaurant_id: str
    total_price: float
    order: list[dict]
    status: str
    latitude: float
    longitude: float
    location: str
    created: datetime

class NewOrder(BaseModel):
    user_id: str
    username: str
    restaurant_id: str
    total_price: float
    latitude: float
    longitude: float
    location: str
    order: list[Item]