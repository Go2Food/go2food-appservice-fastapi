# serialize the collection from json file so its readable by python in a list form
from math import ceil

def individual_serial(account) -> dict:
    return {
        "_id": str(account["_id"]),
        "email": (account["email"]),
        "username": (account["username"]),
        "password":(account["password"]),
    }

def password_protected(account) -> dict:
    return {
        "_id": str(account["_id"]),
        "email": (account["email"]),
        "username": (account["username"]),
        "password": "*********",
        "balance": ceil(account["balance"]*100)/100,
        "premium": (account["premium"]),
    }

def account_id(account) -> dict:
    return {
        "_id": str(account["_id"])
    }


def account_list_serial(accounts) -> list:
    return[individual_serial(account) for account in accounts]

def account_pass_prot_list_serial(accounts) -> list:
    return[password_protected(account) for account in accounts]

def account_id_list_serial(accounts) -> list:
    return[account_id(account) for account in accounts]