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


@router.get("/myposts", 
            response_model=List[schemas.Postbase])
async def get_my_post(db: Session = Depends(get_db), 
                      limit: int = 100, 
                      skip: int = 0, 
                      search: Optional[str] = '',
                      current_user = Depends(oauth2.get_current_user)):
    
    return post.get_my_post(db, limit, skip, search, current_user)


@router.get("/getpost/{group_id}", 
            response_model=List[schemas.Postbase])
async def get_post_in_group(group_id: int, 
                            db: Session = Depends(get_db),
                            current_user = Depends(oauth2.get_current_user)):
    
    return post.get_post_in_group(group_id, db, current_user)



@router.post("/create", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.Postbase)
async def create_post(post_create: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):

    return post.create_post(post_create, db, current_user)


@router.post("/handlepost", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.Postbase)
async def handle_post(post_status: schemas.PostHandle, 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return post.handle_post(post_status, db, current_user)


@router.delete("/delete/{post_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):
    
    return post.delete_post(post_id, db, current_user)


@router.put("/update/{post_id}", 
            response_model=schemas.Postbase)
async def update_post(post_id: int, 
                      newPost: schemas.PostUpdate, 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):
    
    return post.update_post(post_id, newPost, db, current_user)


@router.post("/handlepost/{post_id}")
async def handle_post(post_id: int, 
                      status: str, 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):
    
    return post.handle_post(post_id, status, db, current_user)


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), 
                      db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return post.upload_file(file, db, current_user)


@router.get("/download/")
async def download_file(db: Session = Depends(get_db), 
                      current_user = Depends(oauth2.get_current_user)):

    return post.download_file(db, current_user)


