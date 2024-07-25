from fastapi import status, HTTPException, Depends, APIRouter
from typing import List
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/post", response_model=List[schemas.Post])
async def getPosts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@router.get("/post/{id}", response_model=schemas.Post)
async def getPost(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return post

@router.post("/post", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def createPost(post: schemas.PostCreate, db: Session = Depends(get_db)):
    newPost = models.Post(**post.dict())
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    return newPost

@router.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Succes!"}

@router.put("/post/{id}", response_model=schemas.Post)
async def updatePost(id: int, newPost: schemas.PostCreate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.update(newPost.dict(), synchronize_session=False)
    db.commit()
    return post.first()