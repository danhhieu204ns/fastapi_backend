from fastapi import status, HTTPException
from .. import models, schemas
from sqlalchemy.orm import Session
from typing import Optional


def getGroups(db: Session, 
              limit: int, 
              skip: int, 
              search: Optional[str]):
    
    groups = db.query(models.Group).limit(limit).offset(skip).all()

    return groups


def getgroup(id: int, 
             db: Session,
             current_user):
    
    group = db.query(models.Group).filter(models.Group.id == id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found group with {id}!")
    
    return group


def createGroup(group: schemas.GroupCreate, 
                db: Session, 
                current_user):

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


def re_name(group_id: int, 
                      group_name: schemas.GroupCreate, 
                      db: Session, 
                      current_user):

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


def invite_member(member: schemas.MemberInviteCreate, 
                  db: Session, 
                  current_user):

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

    inviter = db.query(models.Member).filter(models.Member.group_id == member.group_id,
                                             models.Member.user_id == current_user.id, 
                                             models.Member.status == "accepted")
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


def handle_member(invite: schemas.MemberHandle,
                  db: Session, 
                  current_user):

    member_query = db.query(models.Member).filter(models.Member.id == invite.id)
    member = member_query.first()

    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Not found invite!")

    admin = db.query(models.Member).filter(models.Member.group_id == member.group_id,
                                           models.Member.user_id == current_user.id, 
                                           models.Member.role == "admin")
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= "Only admin can handle member!")
    
    member_query.update({models.Member.status: invite.status}, synchronize_session=False)
    db.commit() 
    
    return member_query.first()