from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from schemas.completed_order_schema import completed_order_list_serial
from models.completed_order_model import CompletedOrder, NewOrder, Item
from typing import Annotated, List
from models.model_schemas import GetById, IdLocationForm
from datetime import datetime
from bson import ObjectId
from firebase_admin import storage
import geopy.distance
from math import ceil
from config.mongodbConnection import db
from pymongo import ASCENDING, DESCENDING
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app

router = APIRouter()
collection = db["completed_orders"]
restaurant_collection = db["restaurant"]
user_collection = db["account"]

# get all the accounts as a list
@router.get("/get_completed_orders")
async def get_completed_orders():
    completed_orders = completed_order_list_serial(collection.find())
    return completed_orders

# for user's frontend
@router.post("/get_completed_orders_by_user_id")
async def get_completed_orders_by_user_id(form: GetById):
    form = dict(form)
    id = form.get("id")

    completed_orders = completed_order_list_serial(collection.find({"user_id": id}))
    return completed_orders

# for user's frontend
@router.post("/get_completed_orders_by_user_id_sorted")
async def get_completed_orders_by_user_id_sorted(form: GetById):
    form = dict(form)
    id = form.get("id")

    completed_orders = completed_order_list_serial(collection.find({"user_id": id}).sort({"_id": DESCENDING}))
    return completed_orders

# for restaurant's frontend
@router.post("/get_completed_orders_by_restaurant_id")
async def get_completed_orders_by_restaurant_id(form: GetById):
    form = dict(form)
    id = form.get("id")

    completed_orders = completed_order_list_serial(collection.find({"restaurant_id": id}))
    return completed_orders

# for restaurant's frontend
@router.post("/get_completed_orders_by_restaurant_id_sorted")
async def get_completed_orders_by_restaurant_id_sorted(form: GetById):
    form = dict(form)
    id = form.get("id")

    completed_orders = completed_order_list_serial(collection.find({"restaurant_id": id}).sort({"_id", DESCENDING}))
    return completed_orders

@router.post("/add_completed_order/")
async def add_completed_order(order: CompletedOrder):
    collection.insert_one(order)
    return {"detail": "order is completed"}
    

@router.delete("/delete_completed_order/{id}")
async def delete_completed_order(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
    new_collection = completed_order_list_serial(collection.find())
    return new_collection