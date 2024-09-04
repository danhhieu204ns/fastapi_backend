from fastapi import status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from ..repository import vote


router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def handle_vote(vote_info: schemas.VoteCreate, 
                      db: Session = Depends(database.get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    
    return vote.handle_vote(vote_info, db, current_user)


        
