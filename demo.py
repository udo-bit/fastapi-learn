import json
from uuid import UUID,uuid4
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

app = FastAPI()

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="user_id")
    name: str
    age: int



@app.post("/user/")
def create_user(user: User):
    print(type(jsonable_encoder(user)))
    return user