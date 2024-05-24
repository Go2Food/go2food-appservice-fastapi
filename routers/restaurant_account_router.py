from fastapi import APIRouter
from schemas.restaurant_account_schema import restaurant_account_id_list_serial, restaurant_account_pass_prot_list_serial
from models.account_model import Account
from models.model_schemas import PassCheck, ValidateToken, RestaurantAccountRestaurant, NewRestaurantAccount, GetById
from functions.bcrypt_handler import bcrypt_handler_class
from functions.jwt_authorization import AuthHandler
from bson import ObjectId
from config.mongodbConnection import db
# ignore the unused warning. somehow it will not work if this is not imported even though it is not used directly in the code
from config.firebaseConnection import firebase_storage_app

router = APIRouter()
collection = db["restaurant_accounts"]
bcrypt_handler = bcrypt_handler_class()
jwt_handler = AuthHandler()

# get all the accounts as a list
@router.get("/get_all_restaurant_accounts/")
async def get_all_restaurant_accounts():
    accounts = restaurant_account_pass_prot_list_serial(collection.find())
    return accounts

# get a specific account based on the id
@router.post("/get_restaurant_account_by_id/")
async def get_restaurant_account_by_id(form: GetById):
    user_id = dict(form).get("id")
    account = restaurant_account_pass_prot_list_serial(collection.find({"_id": ObjectId(user_id)}))

    return account

@router.post("/register_restaurant_account/")
async def register_restaurant_account(account: NewRestaurantAccount):
    account = dict(account)
    check = collection.find_one({"email": account.get("email")})

    # return if check is not a none object
    if (check is not None):
        return {"detail": "email already exist"}
    
    try:
        hashed_password = bcrypt_handler.generate_hashedpass(account.get("password"))
        account['password'] = hashed_password
        account['restaurant'] = ""
        collection.insert_one(account)
        return {"detail": "registration success"}
    except:
        return {"detail": "registration failed"}

@router.put("/edit_restaurant_account_restaurant/")
async def edit_restaurant_account_restaurant(form: RestaurantAccountRestaurant):
    form = dict(form)
    account_id = form.get("account_id")
    restaurant_id = form.get("restaurant_id")
    
    collection.find_one_and_update(
            {
                "_id": ObjectId(account_id)
            },
            {
                "$set": {"restaurant": restaurant_id}
            }
        )
    return {"detail": "restaurant account's restaurant succesfully updated"}

# login a user account
@router.post("/login_restaurant_account/")
async def login_restaurant_account(form: PassCheck):
    form = dict(form)
    account = collection.find_one({"email":form.get("email")})
    
    try:
        checkValue = bcrypt_handler.check_password(form.get("password"), account.get("password"))
    except:
        return {"detail": "account not found"}

    if (checkValue):
        restaurant_account = restaurant_account_pass_prot_list_serial(collection.find({"email":form.get("email")}))[0]
        user_id = restaurant_account.get("_id")
        restaurant_id = restaurant_account.get("restaurant")
        print(restaurant_account)
        token = jwt_handler.get_token_restaurant(form.get('email'), user_id, restaurant_id)
        return {"detail": token}
    else:
        return {"detail": "password doesn't match"}
    
    # delete an account (can be both for admin and user if they want to delete their account)
@router.delete("/delete_restaurant_account/")
async def delete_restaurant_account(form: GetById):
    id = dict(form).get("id")
    collection.find_one_and_delete({"_id": ObjectId(id)})

@router.post("/validate_token_restaurant_account/")
async def validate_token_restaurant_account(form: ValidateToken):
    form = dict(form)
    details = jwt_handler.decode_token(form.get("token"))

    if (details):
        return {"detail": details}