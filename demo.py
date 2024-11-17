import json
from typing import List
from uuid import UUID,uuid4
from fastapi import FastAPI, Depends, status, Security, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm,SecurityScopes
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from passlib.hash import bcrypt
from datetime import timedelta,datetime
import jwt
from fastapi import HTTPException
from urllib.parse import quote

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY =  "10fc275baa8f3342a5db16d255c619717d7b7a2063e7843a460ae1d9b09a7c08"
ALGORITHM = "HS256"

fake_users_db = {
    "zhangsan": {
        "username": "zhangsan",
        "full_name": "John Doe",
        "email": "",
        "hashed_password": "$2b$12$kU58HYpOFlWTCKROGP21eOqzMfLMVcGgnMbN0oMczHlaD9uJttA9i",
        "disabled": False},
        
}


app = FastAPI()

oauth2_scheme =  OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items."
    }
)

class User(BaseModel):
    username: str
    email: str|None = None
    full_name: str|None = None
    disabled: bool|None = None

def get_current_user(
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme)
    ):
    print("_"*100)
    print(security_scopes.scope_str)
    print("_"*100)
    try:
        payload = verify_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400,detail="Invalid token")
        token_scopes = payload.get("scopes",[])
        token_data = TokenData(scopes=token_scopes,username=username)
    except Exception as e:
        raise HTTPException(status_code=400,detail="Invalid token")
    print(fake_users_db.get(token_data.username))
    user = User(**fake_users_db.get(token_data.username))
    if user is None:
        raise HTTPException(status_code=400,detail="Invalid token")
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            print(scope)
            raise HTTPException(status_code=400,detail="Not enough permissions")
    return user

def get_current_active_user(current_user: User = Security(get_current_user, scopes=["me"])):
    print(current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactive user")
    return current_user


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
    scopes: List[str] = []

def create_access_token(data:dict,expires_delta:timedelta|None = None):
    print(expires_delta)
    to_encode = data.copy()
    if not expires_delta:
        expire = datetime.now() + timedelta(days=15)
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

@app.get("/items",status_code=status.HTTP_200_OK)
def get_items(user:User = Security(get_current_active_user,scopes=["items"])):
    if user.disabled == True:
        raise HTTPException(status_code=400,detail="Inactive user")
    return user


@app.post("/token")
def logoin(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db,form_data.username,form_data.password)
    if not user:
        return {"error": "Unauthorized"}
    else:
        access_token = create_access_token(data={"sub": user['username'],"scopes": form_data.scopes})
        return Token(access_token=access_token,token_type="bearer")


@app.get("/download")
def download():
    def iterfile():  # (1)
        with open("./01_起步.md", mode="rb") as file_like:  # (2)
            yield from file_like  # (3)

    return StreamingResponse(iterfile(), media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename={quote('01_起步.md')}"})
