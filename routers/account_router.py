from fastapi import APIRouter
from schemas.account_schema import account_list_serial, account_pass_prot_list_serial
from models.account_model import Account
from models.model_schemas import PassCheck, ValidateToken
from functions.bcrypt_handler import bcrypt_handler_class
from functions.jwt_authorization import AuthHandler
from bson import ObjectId
from config.connection import db

router = APIRouter()
collection = db["account"]
bcrypt_handler = bcrypt_handler_class()
jwt_handler = AuthHandler()


# get all the accounts as a list
@router.get("/get_all_accounts")
def get_all_accounts():
    accounts = account_pass_prot_list_serial(collection.find())
    return accounts

# get a specific account based on the id
@router.get("/get_account/{id}")
def get_account(id: str):
    account = account_pass_prot_list_serial(collection.find({"_id": ObjectId(id)}))

    return account

# query account based on username
@router.get("/search_accounts/")
def search_account(username:str):
    accounts = account_pass_prot_list_serial(collection.find({"username":{"$regex":username}}))
    return accounts

# register an account to the database
@router.post("/register/")
async def register(account: Account):
    account = dict(account)
    check = collection.find_one({"email": account.get("email")})

    # return if check is not a none object
    if (check is not None):
        return {"detail": "email already exist"}
    
    try:
        hashed_password = bcrypt_handler.generate_hashedpass(account.get("password"))
        account['password'] = hashed_password
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
        token = jwt_handler.get_token(form.get('email'))
        return {"detail": token}
    else:
        return {"detail": "password doesn't match"}
    
@router.post("/validate_token/")
async def validate_token(form: ValidateToken):
    form = dict(form)
    email = jwt_handler.decode_token(form.get("token"))

    if (email):
        return {"detail": email}


# add new account to the database
@router.post("/add_account")
def add_account(account: Account):
    account = dict(account)
    hashed_password = bcrypt_handler.generate_hashedpass(account.get("password"))
    account['password'] = hashed_password
    collection.insert_one(account)

    return {"message": "Account has been added succesfully"}

# modify an account (for admin maybe idk)
@router.put("/modify_account/{id}")
def modify_account(id: str, account: Account):
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {   
            "$set": dict(account)
        }
    )

    return {"message": "Account has been edited succesfully"}

# edit account email
@router.put("/edit_account_email/{id}")
def edit_account_email(id: str, email: str):
    account = collection.find_one({"_id": ObjectId(id)})
    account["email"] = email
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {   
            "$set": dict(account)
        }
    )

    return {"message": "account email has been changed"}

# edit account username
@router.put("/edit_account_username/{id}")
def edit_account_username(id: str, username: str):
    account = collection.find_one({"_id": ObjectId(id)})
    account["username"] = username
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {   
            "$set": dict(account)
        }
    )

    return {"message": "account username has been changed"}

# edit account password
@router.put("/edit_account_password/{id}")
def edit_account_password(id: str, password: str):
    account = collection.find_one({"_id": ObjectId(id)})
    account["password"] = password
    collection.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {   
            "$set": dict(account)
        }
    )

    return {"message": "account password has been changed"}

# delete an account (can be both for admin and user if they want to delete their account)
@router.delete("/delete_account/{id}")
def delete_account(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})