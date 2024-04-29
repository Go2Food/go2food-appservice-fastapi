from pymongo import MongoClient
from dotenv import load_dotenv
import os

# cuz python env variables do be bullshitting
load_dotenv()

client = MongoClient(os.environ.get('URL'))
database_name = os.environ.get('DATABASE')
db = client.get_database(database_name)