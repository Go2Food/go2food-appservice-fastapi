from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app=app)

# current_temp_account
temp_account_details = {}
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
                "balance": 1000
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
    except KeyError:
        raise ValueError(f"Update location test failed: {id_not_found_err_str}")
    
def test_delete_account():
    try:
        user_id = temp_account_details["user_id"]
        response = client.delete(f"/delete_account/{user_id}", headers=headers)
        assert response.status_code == 200
    except KeyError:
        raise ValueError(f"Delete account test failed: {id_not_found_err_str}")