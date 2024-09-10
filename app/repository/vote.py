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