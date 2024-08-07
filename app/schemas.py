from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class Tokendata(BaseModel):
    id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str
    group_id: int


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    owner: UserResponse
    
    class Config:
        orm_mode = True


class PostVoteResponse(BaseModel):
    Post: PostResponse
    vote: int

    class Config:
        orm_mode = True


class VoteCreate(BaseModel):
    post_id: int
    dir: int