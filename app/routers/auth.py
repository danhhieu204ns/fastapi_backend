from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from ..database import engine, get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["Login"])

@router.post("/login")
async def login_user(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials!")
    return {"message": "Succes!"}