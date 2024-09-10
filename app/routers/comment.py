from fastapi import status, Depends, APIRouter
from typing import List, Optional
from .. import schemas, oauth2
from ..database import get_db
from ..repository import comment
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= "/post",
    tags=["Comments"]
)


@router.get("/{post_id}/comments", 
            status_code=status.HTTP_200_OK, 
            response_model=list[schemas.CommentResponse])
async def get_comment(post_id: int, 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):
    
    return comment.get_comment(post_id, db, current_user)