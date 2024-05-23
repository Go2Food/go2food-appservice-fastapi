from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app=app)

# current_temp_account
temp_account_details = {}
temp_current_resto = {}
temp_current_active_order = {}
headers = {
    "Content-Type": "application/json"
}
id_not_found_err_str = "User ID not found. Possible error on the login validation step"

# random account_generator
# email and username
email = ""
username = ""
sub_domains_count = random.choice([1, 2, 3]) # first part before @, e.g. xxx.xxx@xxx.com
for i in range(sub_domains_count):
    length = random.choice([4, 5, 6, 7, 8, 9, 10]) # letter count in domain, e.g. john.doe@xxx.com
    for j in range(length):
        email += "".join(random.choices(string.ascii_lowercase))
    if i == sub_domains_count - 1:
        username += email
        email += "@example.com"
    else:
        email += random.choice(["-", ".", "_"])
temp_account_details["email"] = email
temp_account_details["username"] = username

# password
pw_length = random.choice([7, 8, 9, 10, 11]) # 7 because 1 character is already added
pw = random.choice(string.ascii_letters)
pw += "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()-_+=", k=pw_length))
temp_account_details["password"] = pw

print("\nGENERATED ACCOUNT DETAILS:")
print(temp_account_details)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smile and Wave Boys!"}
    
def test_register_account():
    response = client.post(
        "/register",
        headers=headers,
        json=temp_account_details
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "registration success"}
    
def test_login():
    login_data = {
        "email": temp_account_details["email"],
        "password": temp_account_details["password"]
    }
    response = client.post(
        "/login",
        headers=headers,
        json=login_data
    )
    assert response.status_code == 200
    assert response.json != {"detail": "account not found"} and response.json != {"detail": "password doesn't match"}
    if (response.status_code == 200):
        formatted_response = response.json()
        temp_account_details["token"] = formatted_response["detail"]
        
def test_validate_login():
    try:
        token = temp_account_details["token"]
        response = client.post(
            "/validate_token",
            headers=headers,
            json={"token": token}
        )
        assert response.status_code == 200
        assert response.json() != {"detail": "Signature has expired"} and response.json != {"detail": "Invalid token"}
        if (response.status_code == 200):
            formatted_response = response.json()
            temp_account_details["user_id"] = formatted_response["detail"]["user_id"]
    except KeyError:
        raise ValueError(f"Validate token test failed: Token not found. Error on the login test step")
    
def test_update_balance():
    try:
        response = client.put(
            "/update_user_balance",
            headers=headers,
            json={
                "id": temp_account_details["user_id"],
                "balance": 1999888777
            }
        )
        assert response.status_code == 200
        assert response.json () == {'detail': 'the balance is updated'}
    except KeyError: 
        raise ValueError(f"Update balance test failed: {id_not_found_err_str}")
    
def test_upgrade_account_type():
    try:
        response = client.post(
            "/update_user_to_premium", 
            headers=headers, 
            json={"id": temp_account_details["user_id"]}
        )
        assert response.status_code == 200
        assert response.json() == {'detail': 'the user is now a premium user'}
    except KeyError:
        raise ValueError(f"Upgrade account test failed: {id_not_found_err_str}")
    
def test_downgrade_account_type():
    try:
        response = client.post(
            "/downgrade_user_from_premium", 
            headers=headers, 
            json={"id": temp_account_details["user_id"]}
        )
        assert response.status_code == 200
        assert response.json() == {'detail': 'the user premium status is downgraded'}
    except KeyError:
        raise ValueError(f"Downgrade account test failed: {id_not_found_err_str}")
    
def test_update_location_lat_lng():
    random_lat = [random.randint(-90, 90) for _ in range(2)]
    random_lat = round(random_lat[0] / random_lat[1], 5)
    random_lng = [random.randint(-180, 180) for _ in range(2)]
    random_lng = round(random_lng[0] / random_lng[1], 5)
    
    try:
        response = client.put(
            "/update_user_location_and_latlong", 
            headers=headers, 
            json={
                "id": temp_account_details["user_id"],
                "location": "Some random place on earth",
                "latitude": random_lat,
                "longitude": random_lng,
            }
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "succesfully set the user's location and lat long"}
        if (response.status_code == 200):
            temp_account_details["lat"] = random_lat
            temp_account_details["lng"] = random_lng
    except KeyError:
        raise ValueError(f"Update location test failed: {id_not_found_err_str}")
    
# TODO: when other restaurants are populated, change the flow to first get all restaurants 
# then randomly choose the restaurant and the menus. 
def test_get_restaurant():
    # for now since the only populated restaurant is this one, we'll hardcode this one first.
    response = client.post(
        "/get_restaurant_byId",
        headers=headers,
        json={
            "id": "663509f0fa0553bc5a34842a",
            "latitude": temp_account_details["lat"],
            "longitude": temp_account_details["lng"]
        }
    )
    assert response.status_code == 200
    if (response.status_code == 200):
        restaurant_data = response.json()
        temp_current_resto["detail"] = restaurant_data
        
def test_get_resto_menu():
    response = client.post(
        "/get_menu_restaurant",
        headers=headers,
        json={
            "id": temp_current_resto["detail"]["_id"]
        }
    )
    assert response.status_code == 200
    if (response.status_code == 200):
        resto_menu = response.json()
        temp_current_resto["menu"] = resto_menu
        
def test_new_order():
    food_to_order = []
    """
    format:
    {
        "item_id": "string",
        "name": "string",
        "amount": 0,
        "price": 0
    }
    """
    
    food_list = temp_current_resto["menu"]
    
    # what menus to choose from the available ones
    mau_makan_apa_aja = random.randint(1, len(food_list))
    total_price = 0
    
    for _ in range(mau_makan_apa_aja):
        random_menu_choose_index = random.randint(0, len(food_list) - 1)
        random_menu_choose = food_list.pop(random_menu_choose_index)
        food_count = random.randint(0, 99)
        price = 0
        for _ in range(food_count):
            price += random_menu_choose["price"]
        food_to_order.append({
            "item_id": random_menu_choose["_id"],
            "name": random_menu_choose["name"],
            "amount": food_count,
            "price": price
        })
        total_price += price
        
    print("\nFOOD TO ORDER:")
    print(food_to_order)
        
    # finally send the request 
    response = client.post(
        "/add_active_order",
        headers=headers,
        json={
            "user_id": temp_account_details["user_id"],
            "username": temp_account_details["username"],
            "restaurant_id": temp_current_resto["detail"]["_id"],
            "total_price": total_price,
            "latitude": temp_account_details["lat"],
            "longitude": temp_account_details["lng"],
            "location": "Somewhere on earth",
            "order": food_to_order
        }
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "active order added succesfully"}

def test_get_active_order_by_resto_id():
    response = client.post(
        "/get_active_order_by_restaurant_id",
        headers=headers,
        json={
            "id": "663509f0fa0553bc5a34842a"
        }
    )
    assert response.status_code == 200
    if (response.status_code == 200):
        formatted_response = response.json()
        temp_current_active_order["detail"] = formatted_response[0]
        
def test_accept_order():
    response = client.put(
        "/accept_pending_order",
        headers=headers,
        json={
            "id": temp_current_active_order["detail"]["_id"]
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list) or response.json() != {"detail": "order is not found on the server"}

def test_deliver_order():
    response = client.put(
        "/deliver_pending_order",
        headers=headers,
        json={
            "id": temp_current_active_order["detail"]["_id"]
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list) or response.json() != {"detail": "order is not found on the server"}
    
def test_delete_pending_finished_order():
    active_order_id = temp_current_active_order['detail']["_id"]
    response = client.delete(
        f"/delete_active_order/{active_order_id}",
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list) or response.json() != {"detail": "no order data is found in the server"}
    
def test_delete_account():
    try:
        user_id = temp_account_details["user_id"]
        response = client.delete(f"/delete_account/{user_id}", headers=headers)
        assert response.status_code == 200
    except KeyError:
        raise ValueError(f"Delete account test failed: {id_not_found_err_str}")