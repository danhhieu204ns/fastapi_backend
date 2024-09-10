from fastapi import status, HTTPException
from .. import schemas, models
from sqlalchemy.orm import Session


def get_comment(post_id: int, 
                db: Session, 
                current_user):
    
    post = db.query(models.Post).filter(models.Post.id == post_id, 
                                        models.Post.status == "accepted").first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found this post")
        
    member = db.query(models.Member).filter(models.Member.group_id == post.group_id, 
                                            models.Member.user_id == current_user.id, 
                                            models.Member.status == "accepted").first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not in this group")
    
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
    
    return comments


def add_comment(new_comment: schemas.CommentCreate, 
                db: Session, 
                current_user):
    
    post = db.query(models.Post).filter(models.Post.id == new_comment.post_id, 
                                        models.Post.status == "accepted").first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found this post")
        
    member = db.query(models.Member).filter(models.Member.group_id == post.group_id, 
                                            models.Member.user_id == current_user.id, 
                                            models.Member.status == "accepted").first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not in this group")
    
    comment = models.Comment(**new_comment.dict(), 
                             user_id = current_user.id)
    db.add(comment)
    db.commit()
    
    return comment

