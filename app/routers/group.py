from fastapi import status, HTTPException, APIRouter, Depends
from .. import models, schemas, utils, database
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

router = APIRouter(
    prefix="/group",
    tags=['Groups']
)

@router.get("/", 
            response_model=List[schemas.GroupResponse])
async def getGroups(db: Session = Depends(database.get_db), 
                   limit: int = 5, 
                   skip: int = 0, 
                   search: Optional[str] = ''):
    
    groups = db.query(models.Group).limit(limit).offset(skip).all()

    return groups