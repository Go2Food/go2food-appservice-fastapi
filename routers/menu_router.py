from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas.menu_schema import menu_list_serial
from models.menu_model import Menu
from models.model_schemas import GetById
from bson import ObjectId
from firebase_admin import storage
from config.mongodbConnection import db
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app

router = APIRouter()
collection = db["menu"]

# get all the accounts as a list
@router.get("/get_all_menus")
async def get_all_menus():
    menus = menu_list_serial(collection.find())
    return menus

@router.post("/get_menu_restaurant")
async def get_menu_restaurant(form: GetById):
    restaurant_id = dict(form).get("id")
    menus = menu_list_serial(collection.find({"restaurant": restaurant_id}))
    return menus

@router.post("/add_menu/")
async def add_menu(file: UploadFile = File(...), restaurant_id: str = "id", name: str = "name", description: str = "description", category: str = "category", price: float = 0):
    if not file.filename.endswith(('.jpg', 'jpeg', 'png')):
        raise HTTPException(status_code=400, detail="Only .jpg .jpeg and .png files are supported")

    picture_id = str(ObjectId())
    # upload the file to the storage
    try:
        path = picture_id + "menu_image"
        bucket = storage.bucket()
        bucket = bucket.blob(path)
        bucket.upload_from_string(await file.read(), content_type=file.content_type)
    except:
        return {"detail": "image upload failed"}
    
    # generate and return the public url of the uploaded file
    url = 'https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media'.format("go2food-67b42.appspot.com", path)
    
    menu = Menu(restaurant=restaurant_id,
                name=name,
                pictureURL=url,
                picture_name=path,
                description=description,
                category=category,
                price=price,
                )

    try:
        collection.insert_one(dict(menu))
        return {"detail": "menu added succesfully"}
    except:
        bucket = storage.bucket()
        bucket = bucket.blob(path)
        bucket.delete()
        return {"detail": "menu addition failed somehow"}
    
@router.delete("/delete_menu/{id}")
async def delete_menu(id: str):
    menu = collection.find_one({"_id": ObjectId(id)})
    image_name = menu["picture_name"]
    try:
        bucket = storage.bucket()
        bucket = bucket.blob(image_name)
        bucket.delete()
        collection.find_one_and_delete({"_id": ObjectId(id)})
        return {"detail": "menu deleted"}
    except Exception as e:
        return {"detail": "menu deletion failed"}
    
@router.delete("/delete_restaurant_menus/{id}")
async def delete_restaurant_menu(id: str):
    menus = collection.find({"restaurant": id})
    for menu in menus:
        try:
            image_name = menu["picture_name"]
            try:
                bucket = storage.bucket()
                bucket = bucket.blob(image_name)
                bucket.delete()
            except:
                return {"detail": "failed while trying to delete image from storage"}
            collection.find_one_and_delete({"_id": ObjectId(menu["_id"])})
        except:
            return {"detail": "deletion failed"}
    return {"detail": "menus deleted"}

    