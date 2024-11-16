import json
from uuid import UUID,uuid4
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from passlib.hash import bcrypt
from datetime import timedelta,datetime
import jwt
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY =  "10fc275baa8f3342a5db16d255c619717d7b7a2063e7843a460ae1d9b09a7c08"
ALGORITHM = "HS256"

fake_users_db = {
    "zhangsan": {
        "username": "zhangsan",
        "full_name": "John Doe",
        "email": "",
        "hashed_password": "$2b$12$kU58HYpOFlWTCKROGP21eOqzMfLMVcGgnMbN0oMczHlaD9uJttA9i"}
}


app = FastAPI()

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    print(token)
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=400,detail="Invalid token data")
    return TokenData(username=username)

def authenticate_user(fake_db,username:str,password:str):
    user = fake_db.get(username)
    if not user:
        return False
    if not pwd_context.verify(password,user['hashed_password']):
        return False
    return user

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username:str

def create_access_token(data:dict,expires_delta:timedelta|None = None):
    print(expires_delta)
    to_encode = data.copy()
    if not expires_delta:
        expire = datetime.now() + timedelta(minutes=15)
        print(expire)
    else:
        expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400,detail="Token expired")
    except jwt.InvalidAlgorithmError:
        raise HTTPException(status_code=400,detail="Invalid token!!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400,detail="Invalid token")
    return payload

@app.get("/items")
def get_items(data:TokenData = Depends(get_current_user)):
    return {"token": data.username}


@app.post("/token")
def logoin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db,form_data.username,form_data.password)
    print(user)
    if not user:
        return {"error": "Unauthorized"}
    else:
        access_token = create_access_token(data={"sub": user['username']})
        return Token(access_token=access_token,token_type="bearer")
    
    
