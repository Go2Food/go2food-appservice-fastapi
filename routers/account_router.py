from fastapi import APIRouter
from schemas.account_schema import account_id_list_serial, account_pass_prot_list_serial
from models.account_model import Account
from models.model_schemas import IdLocationForm, LocationForm, PassCheck, UserBalanceUpdate, UserLocLatLong, UserLocation, ValidateToken, NewAccountGoogle, NewAccount, GetById
from functions.bcrypt_handler import bcrypt_handler_class
from functions.jwt_authorization import AuthHandler
from bson import ObjectId
from config.mongodbConnection import db

router = APIRouter()
collection = db["account"]
bcrypt_handler = bcrypt_handler_class()
jwt_handler = AuthHandler()


# get all the accounts as a list
@router.get("/get_all_accounts")
async def get_all_accounts():
    accounts = account_pass_prot_list_serial(collection.find())
    return accounts

# get a specific account based on the id
@router.post("/get_account_by_id/")
async def get_account_by_id(form: GetById):
    user_id = dict(form).get("id")
    account = account_pass_prot_list_serial(collection.find({"_id": ObjectId(user_id)}))

    return account

# query account based on username
@router.get("/search_accounts/")
async def search_account(username:str):
    accounts = account_pass_prot_list_serial(collection.find({"username":{"$regex":username}}))
    return accounts

# register an account to the database
@router.post("/register/")
async def register(account: NewAccount):
    account = dict(account)
    check = collection.find_one({"email": account.get("email")})

    # return if check is not a none object
    if (check is not None):
        return {"detail": "email already exist"}
    
    try:
        hashed_password = bcrypt_handler.generate_hashedpass(account.get("password"))
        account['password'] = hashed_password
        account["premium"] = False
        account["balance"] = 0.0
        account["location"] = ""
        account["latitude"] = 0
        account["longitude"] = 0
        collection.insert_one(account)
        return {"detail": "registration success"}
    except:
        return {"detail": "registration failed"}
    
# login a user account
@router.post("/login/")
async def login(form: PassCheck):
    form = dict(form)
    account = collection.find_one({"email":form.get("email")})
    
    try:
        checkValue = bcrypt_handler.check_password(form.get("password"), account.get("password"))
    except:
        return {"detail": "account not found"}

    if (checkValue):
        id = account_id_list_serial(collection.find({"email":form.get("email")}))[0].get("_id")
        token = jwt_handler.get_token(form.get('email'), id)
        return {"detail": token}
    else:
        return {"detail": "password doesn't match"}
    
# when logging in using googles sign in with popup
@router.post("/sign-in-google/")
async def SigninWithGoogle(form: NewAccountGoogle):
    form = dict(form)
    account = collection.find_one({"email":form.get("email")})
    
    # if account is already in the database
    if (account is not None):
        id = account_id_list_serial(collection.find({"email":form.get("email")}))[0].get("_id")
        token = jwt_handler.get_token(form.get('email'), id)
        return {"detail": token}
    # if not in database add it to the database
    else:
        try:
            form["premium"] = False
            form["balance"] = 0.0
            form["location"] = ""
            form["latitude"] = 0
            form["longitude"] = 0
            collection.insert_one(form)
        except:
            return {"detail": "sign in failed"}
        id = account_id_list_serial(collection.find({"email":form.get("email")}))[0].get("_id")
        token = jwt_handler.get_token(form.get('email'), id)
        return {"detail": token}

# validate token
@router.post("/validate_token/")
async def validate_token(form: ValidateToken):
    form = dict(form)
    details = jwt_handler.decode_token(form.get("token"))

    if (details):
        return {"detail": details}
    
# get the balance detail of a specific account
@router.post("/get_account_balance_by_id/")
async def get_account_balance_by_id(form: GetById):
    user_id = dict(form).get("id")
    account = collection.find_one({"_id": ObjectId(user_id)})

    return {"detail": account["balance"]}

# update the user account premium status
@router.post("/update_user_to_premium/")
async def update_user_to_premium(form: GetById):
    user_id = dict(form).get("id")
    customer_balance = (collection.find_one({"_id": ObjectId(user_id)}))["balance"]
    new_balance = customer_balance - 9.99
    if new_balance >= 0:
        collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"premium": True, "balance": new_balance}}
        )

        return {"detail": "the user is now a premium user"}

    return {"detail": "insufficient balance"}

# downgrade the user account premium status
@router.post("/downgrade_user_from_premium/")
async def downgrade_user_from_premium(form: GetById):
    user_id = dict(form).get("id")
    collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"premium": False}}
    )

    return {"detail": "the user premium status is downgraded"}

# update the value of balance
@router.put("/update_user_balance/")
async def update_user_balance(form: UserBalanceUpdate):
    user_id = dict(form).get("id")
    balance = dict(form).get("balance")
    
    old_data = collection.find_one({"_id": ObjectId(user_id)})
    new_balance = old_data["balance"] + balance

    collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"balance": new_balance}}
    )

    return {"detail": "the balance is updated"}

# update the location attribute of the user
@router.put("/update_user_location/")
async def update_user_location(form: UserLocation):
    form = dict(form)
    user_id = form.get("id")
    location = form.get("location")
    collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"location": location}}
        )
    return {"detail": "succesfully set the user's location"}

# update the location and lat long attribute of the user
@router.put("/update_user_location_and_latlong/")
async def update_user_location_and_latlong(form: UserLocLatLong):
    form = dict(form)
    user_id = form.get("id")
    location = form.get("location")
    latitude = form.get("latitude")
    longitude = form.get("longitude")
    collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"location": location, "latitude": latitude, "longitude": longitude}}
        )
    return {"detail": "succesfully set the user's location and lat long"}

# update the location attribute of the user
@router.put("/update_user_lat_long/")
async def update_user_lat_long(form: IdLocationForm):
    user_id = dict(form).get("id")
    latitude = dict(form).get("latitude")
    longitude = dict(form).get("longitude")
    collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"latitude": latitude, "longitude": longitude}}
        )
    return {"detail": "succesfully set the user's location"}


# modify an account (for admin maybe idk)
@router.put("/modify_account/{id}")
async def modify_account(id: str, account: Account):
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {   
            "$set": dict(account)
        }
    )

    return {"message": "Account has been edited succesfully"}

# temporary function will probably delete later (if i remember to delete this anyway)
@router.post("/update_accounts")
async def update_accounts():
    update_result = collection.update_many({}, {"$set": {"latitude": 0, "longitude": 0}})
    if update_result.matched_count > 0:
        return {"message": f"{update_result.matched_count} accounts updated successfully."}
    else:
        return {"message": "No accounts found to update."}

# delete an account (can be both for admin and user if they want to delete their account)
@router.delete("/delete_account/{id}")
async def delete_account(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})