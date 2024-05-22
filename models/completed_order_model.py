from pydantic import BaseModel
from datetime import datetime

class Item(BaseModel):
    item_id: str
    name: str
    amount: int
    price: float

class CompletedOrder(BaseModel):
    user_id: str
    username: str
    restaurant_id: str
    restaurant_name: str
    total_price: float
    order: list[dict]
    status: str
    latitude: float
    longitude: float
    completed: datetime

class NewOrder(BaseModel):
    user_id: str
    username: str
    restaurant_id: str
    total_price: float
    latitude: float
    longitude: float
    order: list[Item]