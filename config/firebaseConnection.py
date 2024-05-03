from firebase_admin import credentials, initialize_app
from dotenv import load_dotenv
import os

# cuz python env variables do be bullshitting
load_dotenv()

cred =  credentials.Certificate ({
  "type": os.environ.get("firebase.type"),
  "project_id": os.environ.get("firebase.project_id"),
  "private_key_id": os.environ.get("firebase.private_key_id"),
  "private_key": os.environ.get("firebase.private_key"),
  "client_email": os.environ.get("firebase.client_email"),
  "client_id": os.environ.get("firebase.client_id"),
  "auth_uri": os.environ.get("firebase.auth_uri"),
  "token_uri": os.environ.get("firebase.token_uri"),
  "auth_provider_x509_cert_url": os.environ.get("firebase.auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.environ.get("firebase.client_x509_cert_url"),
  "universe_domain": os.environ.get("firebase.universe_domain"),
})

firebase_storage_app = initialize_app(cred, 
{"storageBucket": os.environ.get("firebase.storageBucket")})