import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import datetime
from dotenv import load_dotenv
import os

# cuz python env variables do be bullshitting
load_dotenv()

class AuthHandler():
    security = HTTPBearer()
    secret = os.environ.get('jwt.secret_key')
    algorithm = os.environ.get('jwt.algorithm')
    validity = datetime.timedelta(hours = 48, minutes = 0, seconds = 0)

    def get_token(self, email, user_id):
        payload = {
            # ignore the fucking deprecated info. Using the not deprecated code on this python function said the method doesnt exist i love python guys why the fuck do i love python so much what the fuck
            "user_id": user_id,
            "email": email,
            "exp": datetime.datetime.utcnow() + self.validity,
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token
    
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("expired")
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            print("invalid")
            raise HTTPException(status_code=401, detail='Invalid Token')
        
    def verify_token(self, auth:HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
    
    def extend_token(self):
        # later (don't know how to yet lmao)
        pass
        