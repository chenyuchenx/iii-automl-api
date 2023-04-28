from pydantic import BaseModel
from typing import Union, Dict, List, Set
from datetime import datetime

class inferItem(BaseModel):
    ts: datetime = None
    value: float = None
    
    class Config:
        schema_extra = {
            "ts": "2023-03-19T04:17:57Z",
            "vlaue": 123
        }

class InferItemListResponse(BaseModel):
    data: List[inferItem] = None
    total: int = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

class DataItem(BaseModel):
    name: str
    source: str
    storage: dict
    type: str

    class Config:
        schema_extra = {
            "example": {
                "name": "MO20230426XXXX",
                "source": "MinIO",
                "storage": {
                    "name": "file 0 04.20.2022-12.27.31.514999_demodevice.csv",
                    "bucketName": "csvdata",
                    "path": "PHM/processed/",
                    "updatedAt": "2022-05-19T09:50:03.306000+00:00",
                    "size": 327
                },
                "type": "csv"
            }
        }
