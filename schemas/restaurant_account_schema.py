def individual_serial(account) -> dict:
    return {
        "_id": str(account["_id"]),
        "email": (account["email"]),
        "restaurant": (account["restaurant"]),
        "password":(account["password"]),
    }

def password_protected(account) -> dict:
    return {
        "_id": str(account["_id"]),
        "email": (account["email"]),
        "restaurant": (account["restaurant"]),
        "password": "*********",
    }

def restaurant_account_id(account) -> dict:
    return {
        "_id": str(account["_id"])
    }


def restaurant_account_list_serial(accounts) -> list:
    return[individual_serial(account) for account in accounts]

def restaurant_account_pass_prot_list_serial(accounts) -> list:
    return[password_protected(account) for account in accounts]

def restaurant_account_id_list_serial(accounts) -> list:
    return[restaurant_account_id(account) for account in accounts]