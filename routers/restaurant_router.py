from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas.restaurant_schema import restaurant_list_serial, restaurant_id_list_serial
from models.restaurant_model import Restaurant
from models.model_schemas import GetById
from bson import ObjectId
from firebase_admin import storage
from config.mongodbConnection import db
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app
from routers.menu_router import delete_restaurant_menu

router = APIRouter()
collection = db["restaurant"]

# get all the accounts as a list
@router.get("/get_all_restaurants")
async def get_all_restaurants():
    restaurants = restaurant_list_serial(collection.find())
    return restaurants

# add a restaurant to the database
@router.post("/add_restaurant/")
async def add_restaurant(file: UploadFile = File(...), restaurant_name: str = "restaurant_name", categories: list[str] = [], longitude: float = 0, latitude: float = 0):
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
                            longitude=longitude,
                            latitude=latitude,
                            rating=0,
                            )
    
    try:
        collection.insert_one(dict(restaurant))
        return {"detail": "restaurant added succesfully"}
    except:
        bucket = storage.bucket()
        bucket = bucket.blob(path)
        bucket.delete()
        return {"detail": "restaurant addition failed somehow"}


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