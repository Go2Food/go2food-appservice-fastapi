# serialize the collection from json file so its readable by python in a list form

def individual_serial(menu) -> dict:
    return {
        "_id": str(menu["_id"]),
        "name": (menu["name"]),
        "pictureURL": (menu["pictureURL"]),
        "description":(menu["description"]),
        "category":(menu["category"]),
        "price":(menu["price"]),
    }

def menu_id(menu) -> dict:
    return {
        "_id": str(menu["_id"])
    }

def menu_list_serial(menus) -> list:
    return[individual_serial(menu) for menu in menus]

def menu_id_list_serial(menus) -> list:
    return[menu_id(menu) for menu in menus]