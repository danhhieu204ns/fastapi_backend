from fastapi import status, Depends, APIRouter, File, UploadFile
from typing import List, Optional
from .. import schemas, oauth2
from ..database import get_db
from ..repository import post
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)



# @router.get("/", response_model=List[schemas.PostVoteResponse])
# async def get_posts(db: Session = Depends(get_db)):
    # return post.get_post(db)


# @router.get("/", 
#             response_model=List[schemas.PostVoteResponse])
# async def get_posts(db: Session = Depends(get_db)):
    # return post.get_posts(db)


@router.get("/", 
            response_model=List[schemas.PostVoteResponse])
async def getPosts(db: Session = Depends(get_db), 
                   limit: int = 100, 
                   skip: int = 0, 
                   search: Optional[str] = ''):
    
    return post.getPosts(db, limit, skip, search)


@router.get("/{id}", 
            response_model=schemas.PostVoteResponse)
async def getPost(id: int, 
                  db: Session = Depends(get_db),
                  current_user = Depends(oauth2.get_current_user)):
    
    return post.getPost(id, db, current_user)


@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.Postbase)
async def createPost(post_create: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    return post.createPost(post_create, db, current_user)


@router.delete("/{id}", 
               status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
    return post.deletePost(id, db, current_user)


@router.put("/{id}", 
            response_model=schemas.Postbase)
async def updatePost(id: int, 
                     newPost: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
    return post.updatePost(id, newPost, db, current_user)


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return post.upload_file(file, db, current_user)


@router.get("/download/")
async def download_file(db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return post.download_file(db, current_user)


