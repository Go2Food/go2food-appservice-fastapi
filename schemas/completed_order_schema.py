def individual_serial(completed_order) -> dict:
    return {
        "_id": str(completed_order["_id"]),
        "user_id": (completed_order["user_id"]),
        "username": (completed_order["username"]),
        "restaurant_id": (completed_order["restaurant_id"]),
        "restaurant_name": (completed_order["restaurant_name"]),
        "total_price": (completed_order["total_price"]),
        "latitude": (completed_order["latitude"]),
        "longitude": (completed_order["longitude"]),
        "order": (completed_order["order"]),
        "status": (completed_order["status"]),
        "completed": (completed_order["completed"]),
    }

def copmleted_order_id(completed_order) -> dict:
    return {
        "_id": str(completed_order["_id"])
    }

def completed_order_list_serial(copmleted_orders) -> list:
    return[individual_serial(copmleted_order) for copmleted_order in copmleted_orders]

def completed_order_id_list_serial(copmleted_orders) -> list:
    return[copmleted_order_id(copmleted_order) for copmleted_order in copmleted_orders]