from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from schemas.active_order_schema import active_order_list_serial
from models.active_order_model import ActiveOrder, NewOrder, Item
from routers.completed_order_router import add_completed_order
from typing import Annotated, List
from models.model_schemas import GetById, IdLocationForm
from datetime import datetime
from bson import ObjectId
from firebase_admin import storage
import geopy.distance
from math import ceil
from config.mongodbConnection import db
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app

router = APIRouter()
collection = db["active_orders"]
restaurant_collection = db["restaurant"]
user_collection = db["account"]

# get all the accounts as a list
@router.get("/get_active_orders")
async def get_active_order():
    active_orders = active_order_list_serial(collection.find())
    return active_orders

@router.post("/get_active_order_by_user_id")
async def get_active_order_by_user_id(form: GetById):
    form = dict(form)
    id = form.get("id")

    active_order = collection.find_one({"user_id": id})
    if active_order is not None:
        now = datetime.now()
        time_diff = now - active_order["created"]
        time_diff = time_diff.total_seconds()
        active_order["_id"] = str(active_order["_id"])

        return active_order
    else:
        return []

# for restaurant frontend
@router.post("/get_active_order_by_restaurant_id")
async def get_active_order_by_restaurant_id(form: GetById):
    form = dict(form)
    id = form.get("id")
    restaurant_data = restaurant_collection.find_one({"_id": ObjectId(id)})
    latitude = restaurant_data["latitude"]
    longitude = restaurant_data["longitude"]


    active_orders = active_order_list_serial(collection.find({"restaurant_id": id}))
    if active_orders is not None:
        for active_order in active_orders:
            distance = geopy.distance.geodesic((latitude, longitude), (active_order['latitude'], active_order['longitude'])).km
            distance = ceil(distance*100)/100
            active_order['distance'] = distance

        return active_orders
    else:
        return []
    
@router.put("/accept_pending_order")
async def accept_pending_order(form: GetById):
    form = dict(form)
    id = form.get("id")
    new_data = collection.find_one({"_id": ObjectId(id)})

    if new_data is not None:
        new_data["status"] = "accepted"
        res = collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": dict(new_data)
        })

        res["_id"] = str(res["_id"])
        return res

    return {"detail": "order is not found on the server"}

@router.put("/reject_pending_order")
async def reject_pending_order(form: GetById):
    form = dict(form)
    id = form.get("id")

    order_data = collection.find_one({"_id": ObjectId(id)})
    user_id = order_data["user_id"]

    new_data = collection.find_one({"_id": ObjectId(id)})

    if new_data is not None:
        new_data["status"] = "rejected"
        # return the balance to the customer who orders
        customer_balance = (user_collection.find_one({"_id": ObjectId(user_id)}))["balance"]
        new_balance = customer_balance + order_data["total_price"]
        user_collection.find_one_and_update (
            {"_id": ObjectId(user_id)},
            {"$set": {"balance": new_balance}}
        )

        res = collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": dict(new_data)
        })

        res["_id"] = str(res["_id"])
        return res

    return {"detail": "order is not found on the server"}

@router.put("/deliver_pending_order")
async def deliver_pending_order(form: GetById):
    form = dict(form)
    id = form.get("id")
    new_data = collection.find_one({"_id": ObjectId(id)})

    if new_data is not None:
        new_data["status"] = "delivered"
        res = collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": dict(new_data)
        })

        res["_id"] = str(res["_id"])
        return res

    return {"detail": "order is not found on the server"}

@router.post("/add_active_order/")
async def add_active_order(
    form: NewOrder
):
    form = dict(form)
    user_id = form.get("user_id")
    username = form.get("username")
    restaurant_id = form.get("restaurant_id")
    total_price = form.get("total_price")
    latitude = form.get("latitude")
    longitude = form.get("longitude")
    check = collection.find_one({"user_id": user_id})

    if check is None:
        customer_balance = (user_collection.find_one({"_id": ObjectId(user_id)}))["balance"]
        if customer_balance < total_price:
            return {"detail": "balance is insufficient"}
        else:
            # update the user balance by deducting the balance by the total price of the order
            new_balance = customer_balance - total_price
            user_collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"balance": new_balance}}
            )
        order = list(form.get("order"))
        list_order = []
        for i in order:
            new_dict = dict(i)
            list_order.append(new_dict)

        active_order = ActiveOrder(
                    user_id=user_id,
                    username=username,
                    restaurant_id=restaurant_id,
                    total_price=total_price,
                    latitude=latitude,
                    longitude=longitude,
                    order=list_order,
                    status="pending",
                    created=datetime.now(),
                    )

        collection.insert_one(dict(active_order))
        return {"detail": "active order added succesfully"}
    else:
        return {"detail": "there is an active order already"}
    
@router.post("/complete_active_order")
async def complete_active_order(form: GetById):
    form = dict(form)
    id = form.get('id')

    active_order_data = collection.find_one({"_id": ObjectId(id)}, {"created": False})
    restaurant_data = restaurant_collection.find_one({"_id": ObjectId(active_order_data["restaurant_id"])})
    active_order_data["status"] = "unrated"
    active_order_data["completed"] = datetime.now()
    active_order_data["restaurant_name"] = restaurant_data["name"]

    if active_order_data is not None:
        await add_completed_order(active_order_data)
        collection.find_one_and_delete({"_id": ObjectId(id)})
        new_collection = active_order_list_serial(collection.find())
        return new_collection
    
    return {"detail": "no order data is found in the server"}

@router.delete("/delete_active_order/{id}")
async def delete_active_order(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
    new_collection = active_order_list_serial(collection.find())
    return new_collection