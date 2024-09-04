from fastapi import status, APIRouter, Depends
from .. import schemas, database, oauth2
from ..repository import group
from sqlalchemy.orm import Session
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
    
    return group.getGroups(db, limit, skip, search)


@router.get("/{id}", 
            response_model=schemas.GroupResponse)
async def getgroup(id: int, 
                   db: Session = Depends(database.get_db),
                   current_user = Depends(oauth2.get_current_user)):

    return group.getgroup(id, db, current_user)


@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.GroupResponse)
async def createGroup(group_info: schemas.GroupCreate, 
                     db: Session = Depends(database.get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    return group.createGroup(group_info, db, current_user)


@router.put("/{group_id}", 
            response_model=schemas.GroupResponse, 
            status_code=status.HTTP_200_OK)
async def update_group_name(group_id: int, 
                            group_name: schemas.GroupCreate, 
                            db: Session = Depends(database.get_db), 
                            current_user = Depends(oauth2.get_current_user)):

    return group(group_id, group_name, db, current_user)


@router.post("/invite",
             response_model= schemas.MemberInviteResponse)
async def invite_member(member: schemas.MemberInviteCreate, 
                        db: Session = Depends(database.get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    return group.invite_member(member, db, current_user)


@router.post("/handlemember",
             response_model= schemas.MemberInviteResponse)
async def handle_member(member: schemas.MemberHandle,
                        db: Session = Depends(database.get_db), 
                        current_user = Depends(oauth2.get_current_user)):
    
    return group.handle_member(member, db, current_user)

