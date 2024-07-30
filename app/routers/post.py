from fastapi import status, HTTPException, Depends, APIRouter
from typing import List
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.Post])
async def getPosts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).all()
    
    return posts

@router.get("/{id}", response_model=schemas.Post)
async def getPost(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def createPost(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    newPost = models.Post(**post.dict())
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    print(current_user.email)
    return newPost

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Succes!"}

@router.put("/{id}", response_model=schemas.Post)
async def updatePost(id: int, newPost: schemas.PostCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.update(newPost.dict(), synchronize_session=False)
    db.commit()
    return post.first()