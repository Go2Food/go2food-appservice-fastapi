# serialize the collection from json file so its readable by python in a list form
from math import ceil

def individual_serial(restaurant) -> dict:
    rating_len = len(restaurant["rating"])
    rating = 0
    if rating_len > 0:
        rating = sum(restaurant["rating"])/len(restaurant["rating"])
        rating = ceil(rating*100)/100
    
    return {
        "_id": str(restaurant["_id"]),
        "name": (restaurant["name"]),
        "pictureURL": (restaurant["pictureURL"]),
        "categories":(restaurant["categories"]),
        "longitude":(restaurant["longitude"]),
        "latitude":(restaurant["latitude"]),
        "rating": rating,
    }

def restaurant_id(restaurant) -> dict:
    return {
        "_id": str(restaurant["_id"])
    }


def restaurant_list_serial(restaurants) -> list:
    return[individual_serial(restaurant) for restaurant in restaurants]

def restaurant_id_list_serial(restaurants) -> list:
    return[restaurant_id(restaurant) for restaurant in restaurants]