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
    
    return group

@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.GroupResponse)
async def createGroup(group: schemas.GroupCreate, 
                     db: Session = Depends(database.get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    new_group = models.Group(**group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    admin = models.Member(user_id = current_user.id, 
                          group_id = new_group.id, 
                          inviter_id = current_user.id, 
                          status = "accepted", 
                          role = "admin")
    db.add(admin)
    db.commit()

    return new_group

@router.put("/{group_id}", 
            response_model=schemas.GroupResponse, 
            status_code=status.HTTP_200_OK)
async def update_group_name(group_id: int, 
                            group_name: schemas.GroupCreate, 
                            db: Session = Depends(database.get_db), 
                            current_user = Depends(oauth2.get_current_user)):

    group = db.query(models.Group).filter(models.Group.id == group_id)

    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Not found group with id = {group_id}")
    
    admin = db.query(models.Member).filter(models.Member.group_id == group_id,
                                          models.Member.user_id == current_user.id, 
                                          models.Member.role == "admin")

    if not admin.first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Only admin can rename group!")
    
    group.update(group_name.dict(), synchronize_session=False)

    db.commit()

    return group.first()


@router.post("/invite",
             response_model= schemas.MemberInviteResponse)
async def invite_member(member: schemas.MemberInviteCreate, 
                        db: Session = Depends(database.get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    user = db.query(models.User).filter(models.User.id == member.user_id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Not found user with id = {member.user_id}")

    group = db.query(models.Group).filter(models.Group.id == member.group_id)

    if not group.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Not found group with id = {member.group_id}")

    this_member = db.query(models.Member).filter(models.Member.group_id == member.group_id,
                                                 models.Member.user_id == member.user_id)

    if this_member.first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= f"Id = {member.user_id} has already exist in this group")

    inviter = db.query(models.Member).filter(models.Member.user_id == current_user.id, 
                                             models.Member.group_id == member.group_id)
    
    if not inviter.first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= f"You are not in this group")

    member_status = "waiting"

    if inviter.first().role == "admin":
        member_status = "accepted"
        
    new_member = models.Member(**member.dict(), 
                               status = member_status, 
                               role = "member",
                               inviter_id = current_user.id)

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


@router.post("/handlemember",
             response_model= schemas.MemberInviteResponse)
async def handle_member(member: schemas.MemberHandle,
                        db: Session = Depends(database.get_db), 
                        current_user = Depends(oauth2.get_current_user)):

    admin = db.query(models.Member).filter(models.Member.user_id == current_user.id, 
                                           models.Member.group_id == member.group_id, 
                                           models.Member.role == "admin")

    if not admin.first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= "Only admin can accept member!")

    this_member = db.query(models.Member).filter(models.Member.user_id == member.user_id, 
                                                 models.Member.group_id == member.group_id)

    if not this_member.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Not found this member")
    
    this_member.update({models.Member.status: member.status}, synchronize_session=False)
    db.commit() 
    
    return this_member.first()