from fastapi import status, HTTPException
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from sqlalchemy import event
import re


event.listen(models.User, 'before_insert', models.User.before_insert)
event.listen(models.User, 'before_update', models.User.before_update)

def create_user(user: schemas.UserCreate, 
                db: Session):
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


def get_user_byid(id: int, 
                  db: Session):
    
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found user with id = {id}")
    
    return user


def updateUser(newUser: schemas.UserUpdate, 
               db: Session, 
               current_user):

    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    for key, value in newUser.dict().items():
        setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    # user.update(newUser.dict(), synchronize_session=False)
    # db.commit()
    
    return user