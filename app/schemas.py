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
    date_of_birth: Optional[str] = None
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
    privacy: str
    group_id: int


class Postbase(BaseModel):
    id: int
    title: str
    content: str
    group_id: int
    status: Optional[str]

    owner: UserResponse
    
    class Config:
        orm_mode = True


class PostVoteResponse(BaseModel):
    Post: Postbase
    vote: int

    class Config:
        orm_mode = True


class VoteCreate(BaseModel):
    post_id: int
    dir: int


class GroupCreate(BaseModel):
    name: str


class GroupResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        orm_mode = True


class MemberInviteCreate(BaseModel):
    user_id: int
    group_id: int

class MemberInviteResponse(BaseModel):
    id: int
    user_id: int
    group_id: int
    inviter_id: int
    status: str

    class Config:
        orm_mode = True


class MemberHandle(BaseModel):
    user_id: int
    group_id: int
    status: str


