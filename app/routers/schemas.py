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
