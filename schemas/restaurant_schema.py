# serialize the collection from json file so its readable by python in a list form

def individual_serial(restaurant) -> dict:
    return {
        "_id": str(restaurant["_id"]),
        "name": (restaurant["name"]),
        "pictureURL": (restaurant["pictureURL"]),
        "categories":(restaurant["categories"]),
        "longitude":(restaurant["longitude"]),
        "latitude":(restaurant["latitude"]),
        "rating":(restaurant["rating"]),
    }

def restaurant_id(restaurant) -> dict:
    return {
        "_id": str(restaurant["_id"])
    }


def restaurant_list_serial(restaurants) -> list:
    return[individual_serial(restaurant) for restaurant in restaurants]

def restaurant_id_list_serial(restaurants) -> list:
    return[restaurant_id(restaurant) for restaurant in restaurants]