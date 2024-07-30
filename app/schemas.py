from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    create_at: datetime
    
    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str
    owner_id: int

    owner: UserResponse
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Tokendata(BaseModel):
    id: Optional[int] = None