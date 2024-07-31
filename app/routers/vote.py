from fastapi import status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.VoteCreate, 
               db: Session = Depends(database.get_db), 
               current_user: int = Depends(oauth2.get_current_user)):
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    vote_found = vote_query.first()

    if vote.dir == 1:
        if vote_found:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Unliked"}
        else:
            new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
            db.add(new_vote)
            db.commit()
            return {"message": "Liked"}
    else:
        if vote_found:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Unliked"}
        
