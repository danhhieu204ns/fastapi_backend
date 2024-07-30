from fastapi import status, HTTPException, Depends, APIRouter
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostResponse])
async def getPosts(db: Session = Depends(get_db), 
                   limit: int = 5, 
                   skip: int = 0, 
                   search: Optional[str] = ''):
    
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.get("/{id}", response_model=schemas.PostResponse)
async def getPost(id: int, 
                  db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowed post with {id}!")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def createPost(post: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user: int = Depends(oauth2.get_current_user)):
    
    newPost = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    return newPost

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, 
                     db: Session = Depends(get_db), 
                     current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowed post with {id}!")
    
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Succes!"}

@router.put("/{id}", response_model=schemas.PostResponse)
async def updatePost(id: int, 
                     newPost: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowwed post with {id}!")
    
    post.update(newPost.dict(), synchronize_session=False)
    db.commit()
    return post.first()