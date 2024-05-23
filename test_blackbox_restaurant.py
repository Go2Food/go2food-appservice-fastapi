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

categories = ["burgers", "chickens", "asians", "seafood", "pizzas", "beverages"]

random_lat = [random.randint(-90, 90) for _ in range(2)]
random_lng = [random.randint(-180, 180) for _ in range(2)]

random_lat = round(random_lat[0] / random_lat[1], 5)
random_lng = round(random_lng[0] / random_lng[1], 5)
random_restaurant_name = random.choices(string.ascii_letters, k=15)
random_category = categories[random.randint(0, len(categories) - 1)]