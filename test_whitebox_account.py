from fastapi.testclient import TestClient
from main import app
from pytest import raises

client = TestClient(app=app)

# current_temp_account
temp_account_details = {
    "email": "whiteboxtesting@example.com",
    "username": "whiteboxtesting",
    "password": "whiteboxtesting"
}
headers = {
    "Content-Type": "application/json"
}
id_not_found_err_str = "User ID not found. Possible error on the login validation step"

# register 
def test_register_account_email_exists():
    response = client.post(
        "/register",
        headers=headers,
        json=temp_account_details
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "email already exist"}
    
# login
def login(email, password):
    login_data = {
        "email": email,
        "password": password
    }
    response = client.post(
        "/login",
        headers=headers,
        json=login_data
    )
    return response

def test_login_password_wrong():
    response = login(temp_account_details["email"], "deliberatelywrongpassword")
    assert response.status_code == 200
    assert response.json() == {"detail": "password doesn't match"}
    
def test_login_account_not_found():
    reponse = login("deliberatelywrongemail@example.com", temp_account_details["password"])
    assert reponse.status_code == 200
    assert reponse.json() == {"detail": "account not found"}
    
def test_login_successful():
    response = login(temp_account_details["email"], temp_account_details["password"])
    assert response.status_code == 200
    assert response.json() != {"detail": "Signature has expired"} and response.json != {"detail": "Invalid token"}
    if (response.status_code == 200):
        formatted_response = response.json()
        temp_account_details["token"] = formatted_response["detail"]
        
# token
def validate_token(token):
    response = client.post(
            "/validate_token",
            headers=headers,
            json={"token": token}
        )
    return response
            
def test_invalid_token():
    token = str(temp_account_details["token"]).replace(".", " ")
    response = validate_token(token)
    assert response.status_code == 401

def test_valid_token():
    token = temp_account_details["token"]
    response = validate_token(token)
    assert response.status_code == 200
    assert response.json() != {"detail": "Signature has expired"} and response.json != {"detail": "Invalid token"}
    if (response.status_code == 200):
        formatted_response = response.json()
        temp_account_details["user_id"] = formatted_response["detail"]["user_id"]
        
# user details
def test_badrequest_updatebalance():
    with raises(Exception) as bsonInvalidId:
        response = client.put(
            "/update_user_balance",
            headers=headers,
            json={
                "id": temp_account_details["user_id"] + "deliberatelywrongid",
                "balance": 1000
            }
        )
        assert response.status_code == 500

def test_badrequest_upgradeaccounttype():
    with raises(Exception) as bsonInvalidId:
        response = client.post(
            "/update_user_to_premium", 
            headers=headers, 
            json={
                "id": temp_account_details["user_id"] + "deliberatelywrongid"
            }
        )
        assert response.status_code == 500

    
def test_badrequest_downgradeaccounttype():
    with raises(Exception) as bsonInvalidId:
        response = client.post(
            "/downgrade_user_from_premium", 
            headers=headers, 
            json={
                "id": temp_account_details["user_id"] + "deliberatelywrongid"
            }
        )
        assert response.status_code == 500
