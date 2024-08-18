from fastapi import status, HTTPException, APIRouter, Depends
from .. import models, schemas, utils, database, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import event
from datetime import datetime, date
import re

router = APIRouter(
    prefix= "/user",
    tags=["Users"]
)

event.listen(models.User, 'before_insert', models.User.before_insert)
event.listen(models.User, 'before_update', models.User.before_update)

@router.post("/register", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, 
                      db: Session = Depends(database.get_db)):
    
    username = db.query(models.User).filter(models.User.email == user.email).first()
    if username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Email is already exist.")
    
    if user.password.__len__() < 8:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one uppercase letter.")

    if not re.search(r'[a-z]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one lowercase letter.")
    
    if not re.search(r'[0-9]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one number.")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Password must contain at least one special character.")
    
    # date_format = "%Y-%m-%d"
    # age = utils.calculate_age(user.date_of_birth, date.today())

    user.password = utils.hash(user.password)
    newUser = models.User(**user.dict())
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return newUser

@router.get("/{id}", 
            response_model=schemas.UserResponse)
async def get_user_byid(id: int, 
                        db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found user with id = {id}")
    
    return user


@router.put("/", 
            response_model=schemas.UserResponse)
async def updateUser(newUser: schemas.UserUpdate, 
                     db: Session = Depends(database.get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    for key, value in newUser.dict().items():
        setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)

    # user.update(newUser.dict(), synchronize_session=False)
    # db.commit()
    
    return user