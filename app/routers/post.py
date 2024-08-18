from fastapi import status, HTTPException, Depends, APIRouter, File, UploadFile
from fastapi.responses import HTMLResponse
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)

def fetch_data_in_thread(db: Session, start: int, end: int, result: list):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
    posts = posts.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    posts = posts.filter(models.Post.id >= start, models.Post.id < end)
    
    result.extend(posts.all())

@router.get("/", response_model=List[schemas.PostVoteResponse])
async def get_posts(db: Session = Depends(get_db)):
    num_threads = 10

    try:
        num_records = db.query(func.count(models.Post.id)).scalar()
        if num_records == 0:
            return []

        records_per_thread = num_records // num_threads
        threads = []
        results = [[] for _ in range(num_threads)]
        
        for i in range(num_threads):
            start = i * records_per_thread
            end = min((i + 1) * records_per_thread, num_records)
            thread = threading.Thread(target=fetch_data_in_thread, args=(db, start, end, results[i]))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        flattened_results = [item for sublist in results for item in sublist]
        return flattened_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

# async def fetch_data_in_thread(db: Session, start: int, end: int):
#     posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
#     posts = posts.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
#     posts = posts.filter(models.Post.id >= start,
#                          models.Post.id < end)
    
#     with ThreadPoolExecutor() as executor:
#         future = executor.submit(db.execute, posts)
#         result = future.result()
#         rows = result.fetchall()
#         return rows

# @router.get("/", 
#             response_model=List[schemas.PostVoteResponse])
# async def get_posts(db: Session = Depends(get_db)):
#     num_threads = 5

#     try:
#         num_records = db.query(func.count(models.Post.id)).scalar()
#         if num_records == 0:
#             return []

#         records_per_thread = num_records // num_threads
#         tasks = []
#         for i in range(num_threads):
#             start = i * records_per_thread
#             end = min((i + 1) * records_per_thread, num_records)
#             task = asyncio.create_task(fetch_data_in_thread(db, start, end))
#             tasks.append(task)

#         results = await asyncio.gather(*tasks)
#         flattened_results = [item for sublist in results for item in sublist]
#         return flattened_results

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


# @router.get("/", 
#             response_model=List[schemas.PostVoteResponse])
# async def getPosts(db: Session = Depends(get_db), 
#                    limit: int = 100, 
#                    skip: int = 0, 
#                    search: Optional[str] = ''):
    
#     posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
#     posts = posts.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
#     posts = posts.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

#     return posts

@router.get("/{id}", 
            response_model=schemas.PostVoteResponse)
async def getPost(id: int, 
                  db: Session = Depends(get_db),
                  current_user = Depends(oauth2.get_current_user)):
    
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
    post = post.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post = post.filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    
    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowed post with {id}!")
    
    return post

@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.Postbase)
async def createPost(post_create: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
    group = db.query(models.Group).filter(models.Group.id == post_create.group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Group with id = {post_create.group_id} is not exist!!")

    user = db.query(models.Member).filter(models.Member.group_id == post_create.group_id, 
                                          models.Member.user_id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not a member of this group!")
    
    if user.status != "accepted":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not accepted to this group!")

    newPost = models.Post(**post_create.dict(), user_id=current_user.id)
    db.add(newPost)
    db.commit()

    return newPost

@router.delete("/{id}", 
               status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
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

@router.put("/{id}", 
            response_model=schemas.Postbase)
async def updatePost(id: int, 
                     newPost: schemas.PostCreate, 
                     db: Session = Depends(get_db), 
                     current_user = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    
    if post.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowwed post with {id}!")
    
    post.update(newPost.dict(), synchronize_session=False)
    db.commit()
    
    return post.first()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Bạn có thể xử lý file ở đây (ví dụ: lưu vào đĩa, đọc nội dung, v.v.)
    return {"filename": file.filename, 
            "content": contents}

@router.get("/")
async def main():
    content = """
    <body>
    <form action="/upload/" enctype="multipart/form-data" method="post">
    <input name="file" type="file">
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content)