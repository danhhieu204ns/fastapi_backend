from fastapi import status, HTTPException, APIRouter, Depends
from .. import models, schemas, utils, database, oauth2
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

@router.get("/{id}", 
            response_model=schemas.GroupResponse)
async def getgroup(id: int, 
                  db: Session = Depends(database.get_db),
                  current_user = Depends(oauth2.get_current_user)):
    
    group = db.query(models.Group).filter(models.Group.id == id).first()

    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found group with {id}!")
    
    if group.admin_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not allowed group with {id}!")
    
    return group

@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.GroupResponse)
async def createGroup(group: schemas.GroupCreate, 
                     db: Session = Depends(database.get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    new_group = models.Group(**group.dict(), admin_id=current_user.id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group