from fastapi.testclient import TestClient

from main import app

client = TestClient(app=app)

# current_temp_account
temp_account_details = {}
headers = {
    "Content-Type": "application/json"
}
id_not_found_err_str = "User ID not found. Possible error on the login validation step"

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smile and Wave Boys!"}
    
def test_register_account():
    temp_account_details["email"] = "tobrutenak@gmail.com"
    temp_account_details["username"] = "tobrutenakbanget"
    temp_account_details["password"] = "tobrutenakbanget"
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
        assert response.json () == {}
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
        assert response.json() == {}
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
    
def test_delete_account():
    try:
        user_id = temp_account_details["user_id"]
        response = client.delete(f"/delete_account/{user_id}", headers=headers)
        assert response.status_code == 200
    except KeyError:
        raise ValueError(f"Delete account test failed: {id_not_found_err_str}")