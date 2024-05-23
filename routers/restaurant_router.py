from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas.restaurant_schema import restaurant_list_serial, restaurant_id_list_serial
from models.restaurant_model import Restaurant
from models.model_schemas import GetById, LocationForm, IdLocationForm, RestaurantQuery, RestaurantRating
from bson import ObjectId
from firebase_admin import storage
from config.mongodbConnection import db
from routers.menu_router import delete_restaurant_menu
from pymongo import ASCENDING, DESCENDING
import geopy.distance
from math import ceil
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app

router = APIRouter()
collection = db["restaurant"]
completed_order_collection = db["completed_orders"]

# get all the restaurants
@router.get("/get_all_restaurants/")
async def get_all_restaurants():
    restaurants = restaurant_list_serial(collection.find())
    return restaurants

# this is for customer frontend
@router.post("/get_restaurant_byId/")
async def get_restaurant_byId(form: IdLocationForm):
    form = dict(form)
    restaurant_id = form.get("id")
    latitude = form.get("latitude")
    longitude = form.get("longitude")
    restaurant = collection.find_one({"_id": ObjectId(restaurant_id)})
    restaurant["_id"] = str(restaurant["_id"])
    distance = geopy.distance.geodesic((latitude, longitude), (restaurant['latitude'], restaurant['longitude'])).km
    distance = ceil(distance*100)/100
    restaurant['distance'] = distance
    rating = (sum(restaurant["rating"])/len(restaurant["rating"])) if len(restaurant["rating"]) > 0 else 0
    rating = ceil(rating*100)/100
    restaurant["rating"] = rating
    
    return restaurant

# this is for restaurant frontend (to be shown in their dashboard so they can edit their restaurant menus or information if it'll ever get to that)
@router.post("/get_restaurant_byId_restaurant_account/")
async def get_restaurant_byId_restaurant_account(form: GetById):
    form = dict(form)
    restaurant_id = form.get("id")
    restaurant = collection.find_one({"_id": ObjectId(restaurant_id)})
    restaurant["_id"] = str(restaurant["_id"])
    rating = (sum(restaurant["rating"])/len(restaurant["rating"])) if len(restaurant["rating"]) > 0 else 0
    rating = ceil(rating*100)/100
    restaurant["rating"] = rating
    
    return restaurant
    
# get restaurants to be shown in the recommended list on the dashboard page of the frontend app of gofood2
@router.post("/get_recommended_restaurants/")
async def get_recommended_restaurants(form: LocationForm):
    form = dict(form)
    restaurants = restaurant_list_serial(collection.find())
    for restaurant in restaurants:
        distance = geopy.distance.geodesic((form.get('latitude'), form.get("longitude")), (restaurant['latitude'], restaurant['longitude'])).km
        distance = ceil(distance*100)/100
        restaurant['distance'] = distance
    return restaurants

@router.put("/update_restaurant_rating")
async def update_restaurant_rating(form: RestaurantRating):
    form = dict(form)
    id = form.get("id")
    order_id = form.get("order_id")
    rating = form.get("rating")
    current_restaurant_data = collection.find_one({"_id": ObjectId(id)})
    curr_rating = current_restaurant_data["rating"]
    curr_rating.append(rating)
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        }, 
        {
            "$set": {"rating": curr_rating}
        })
    completed_order_collection.find_one_and_update(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "rated", "rating": rating}}
    )
    return {"detail": "data updated"}

@router.post("/get_restaurants_based_on_query")
async def get_restaurants_based_on_query(form: RestaurantQuery):
    form = dict(form)
    name = form.get("search_name")
    tags = form.get("tags")
    currentpage = form.get("currentpage")
    itemperpage = form.get("itemperpage")
    radius = form.get("radius")
    rating_treshold = form.get("rating_treshold")
    print(rating_treshold)
    print(radius)
    start = (currentpage - 1) * itemperpage
    end = start + itemperpage
    search_result = []
    if tags != []:
        restaurants = restaurant_list_serial(collection.find({"name":{"$regex":name, "$options": "i"}, "categories": {"$in": tags}}))
    else:
        restaurants = restaurant_list_serial(collection.find({"name":{"$regex":name, "$options": "i"}}))

    for restaurant in restaurants:
        distance = geopy.distance.geodesic((form.get('latitude'), form.get("longitude")), (restaurant['latitude'], restaurant['longitude'])).km
        distance = ceil(distance*100)/100
        restaurant['distance'] = distance
        if (radius != -1 and distance > radius):
            continue
        if (rating_treshold != -1 and rating_treshold > restaurant["rating"]):
            continue
        search_result.append(restaurant)
    
    final_res = sorted(search_result, key=lambda item: (-item['rating'], item['distance']))
    max_page = -(len(final_res) // -itemperpage)
    return {"max_page": max_page, "datas": final_res[start:end]}

# get restaurants to be shown in the recommended list on the dashboard page of the frontend app of gofood2
@router.post("/get_recommended_restaurants_sorted/")
async def get_recommended_restaurants_sorted(form: LocationForm):
    form = dict(form)
    restaurants = restaurant_list_serial(collection.find())
    for restaurant in restaurants:
        distance = geopy.distance.geodesic((form.get('latitude'), form.get("longitude")), (restaurant['latitude'], restaurant['longitude'])).km
        distance = ceil(distance*100)/100
        restaurant['distance'] = distance
    return sorted(restaurants, key=lambda item: (-item['rating'], item['distance']))

@router.post("/get_recent_restaurants/")
async def get_recent_restaurants(form: IdLocationForm):
    form = dict(form)
    user_id = form.get("id")
    recent_orders_datas = completed_order_collection.find({"user_id": user_id})
    restaurant_ids = []
    if recent_orders_datas is not None:
        for recent_orders_data in recent_orders_datas:
            recent_orders_data = dict(recent_orders_data)
            restaurant_ids.append(ObjectId(recent_orders_data["restaurant_id"]))
        
        restaurants = []
        for restaurant_id in restaurant_ids:
            restaurant = collection.find_one({"_id": restaurant_id})
            restaurant["_id"] = str(restaurant["_id"])
            distance = geopy.distance.geodesic((form.get('latitude'), form.get("longitude")), (restaurant['latitude'], restaurant['longitude'])).km
            distance = ceil(distance*100)/100
            restaurant['distance'] = distance
            rating = (sum(restaurant["rating"])/len(restaurant["rating"])) if len(restaurant["rating"]) > 0 else 0
            rating = ceil(rating*100)/100
            restaurant["rating"] = rating
            restaurants.append(restaurant)

        return restaurants
    return []

@router.post("/get_recent_restaurants_sorted/")
async def get_recent_restaurants_sorted(form: IdLocationForm):
    form = dict(form)
    user_id = form.get("id")
    recent_orders_datas = completed_order_collection.find({"user_id": user_id}).sort({"_id": DESCENDING})
    restaurant_ids = []
    if recent_orders_datas is not None:
        for recent_orders_data in recent_orders_datas:
            recent_orders_data = dict(recent_orders_data)
            restaurant_ids.append(ObjectId(recent_orders_data["restaurant_id"]))
        
        restaurants = []
        for restaurant_id in restaurant_ids:
            restaurant = collection.find_one({"_id": restaurant_id})
            restaurant["_id"] = str(restaurant["_id"])
            distance = geopy.distance.geodesic((form.get('latitude'), form.get("longitude")), (restaurant['latitude'], restaurant['longitude'])).km
            distance = ceil(distance*100)/100
            restaurant['distance'] = distance
            rating = (sum(restaurant["rating"])/len(restaurant["rating"])) if len(restaurant["rating"]) > 0 else 0
            rating = ceil(rating*100)/100
            restaurant["rating"] = rating
            restaurants.append(restaurant)

        return restaurants[0:8]
    return []

# add a restaurant to the database
@router.post("/add_restaurant/")
async def add_restaurant(file: UploadFile = File(...), restaurant_name: str = "restaurant_name", categories: list[str] = [], latitude: float = 0, longitude: float = 0):
    if not file.filename.endswith(('.jpg', 'jpeg', 'png')):
        raise HTTPException(status_code=400, detail="Only .jpg .jpeg and .png files are supported")

    restaurant_id = str(ObjectId())
    # upload the file to the storage
    try:
        path = restaurant_id + "restaurant_image"
        bucket = storage.bucket()
        bucket = bucket.blob(path)
        bucket.upload_from_string(await file.read(), content_type=file.content_type)
    except:
        return {"detail": "image upload failed"}
    
    # generate and return the public url of the uploaded file
    url = 'https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media'.format("go2food-67b42.appspot.com", path)

    # soalnya tolol mongodb atau fast api tololah intinya salah satu dari mereka
    new_list = [item.strip() for item in categories[0].split(",")]
    
    restaurant = Restaurant(name=restaurant_name,
                            pictureURL=url,
                            picture_name=path,
                            categories=new_list,
                            latitude=latitude,
                            longitude=longitude,
                            rating=[],
                            )
    
    try:
        collection.insert_one(dict(restaurant))
        return {"detail": "restaurant added succesfully"}
    except:
        bucket = storage.bucket()
        bucket = bucket.blob(path)
        bucket.delete()
        return {"detail": "restaurant addition failed somehow"}

# this is for refactoring the restaurant database (will probably delete later if i ever remember to delete this later)
@router.post("/update_restaurants")
async def update_restaurants():
    update_result = collection.update_many({}, {"$set": {"rating": []}})
    if update_result.matched_count > 0:
        return {"message": f"{update_result.matched_count} restaurants updated successfully."}
    else:
        return {"message": "No restaurants found to update."}

@router.delete("/delete_restaurant/{id}")
async def delete_restaurant(id: str):
    res = await delete_restaurant_menu(id)
    if res.get("detail") == "menus deleted":
        restaurant = collection.find_one({"_id": ObjectId(id)})
        image_name = restaurant["picture_name"]
        try:
            bucket = storage.bucket()
            bucket = bucket.blob(image_name)
            bucket.delete()
            collection.find_one_and_delete({"_id": ObjectId(id)})
            return {"detail": "restaurant deleted"}
        except Exception as e:
            return {"detail": "restaurant deletion failed"}