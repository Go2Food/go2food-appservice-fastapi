def individual_serial(order) -> dict:
    return {
        "_id": str(order["_id"]),
        "user_id": (order["user_id"]),
        "username": (order["username"]),
        "restaurant_id": (order["restaurant_id"]),
        "total_price": (order["total_price"]),
        "latitude": (order["latitude"]),
        "longitude": (order["longitude"]),
        "location": (order["location"]),
        "order": (order["order"]),
        "status": (order["status"]),
        "created": (order["created"]),
    }

def active_order_id(order) -> dict:
    return {
        "_id": str(order["_id"])
    }

def active_order_list_serial(orders) -> list:
    return[individual_serial(order) for order in orders]

def order_id_list_serial(orders) -> list:
    return[active_order_id(order) for order in orders]