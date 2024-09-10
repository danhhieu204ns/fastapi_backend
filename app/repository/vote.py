from fastapi import status, HTTPException
from .. import schemas, models
from sqlalchemy.orm import Session


def handle_vote(vote: schemas.VoteCreate, 
                db: Session, 
                current_user):
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, 
                                              models.Vote.user_id == current_user.id)
    vote_found = vote_query.first()
    
    message = ""

    if vote.dir == 1:
        if vote_found:
            vote_query.delete(synchronize_session=False)
            db.commit()
            message = "Unliked"
        else:
            new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
            db.add(new_vote)
            db.commit()
            message = "Liked"
    else:
        if vote_found:
            vote_query.delete(synchronize_session=False)
            db.commit()
            message = "Unliked"
        
    return {"message": message}


def get_vote_list(post_id: int, 
                  db: Session, 
                  current_user):
    
    post = db.query(models.Post).filter(models.Post.id == post_id, 
                                        models.Post.status == "accepted").first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found")
        
    member = db.query(models.Member).filter(models.Member.group_id == post.group_id, 
                                            models.Member.user_id == current_user.id, 
                                            models.Member.status == "accepted").first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not in this group")
    
    votes = db.query(models.Vote).filter(models.Vote.post_id == post_id).all()
    
    return votes
