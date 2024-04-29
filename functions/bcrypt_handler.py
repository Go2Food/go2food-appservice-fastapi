import bcrypt

class bcrypt_handler_class():
    def generate_hashedpass(self, password:str):
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        return hashed_pw
    
    def check_password(self, password:str, hashed_password:str):
        return bcrypt.checkpw(password.encode(), hashed_password.encode())