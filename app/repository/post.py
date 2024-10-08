from fastapi import status, HTTPException, Depends, UploadFile
from typing import Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from fastapi.responses import FileResponse


# def fetch_data_in_thread(db: Session, start: int, end: int, result: list):
#     posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
#     posts = posts.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
#     posts = posts.filter(models.Post.id >= start, models.Post.id < end)
    
#     result.extend(posts.all())

# def get_posts(db: Session):
#     num_threads = 10

#     try:
#         num_records = db.query(func.count(models.Post.id)).scalar()
#         if num_records == 0:
#             return []

#         records_per_thread = num_records // num_threads
#         threads = []
#         results = [[] for _ in range(num_threads)]
        
#         for i in range(num_threads):
#             start = i * records_per_thread
#             end = min((i + 1) * records_per_thread, num_records)
#             thread = threading.Thread(target=fetch_data_in_thread, args=(db, start, end, results[i]))
#             threads.append(thread)
#             thread.start()

#         for thread in threads:
#             thread.join()

#         flattened_results = [item for sublist in results for item in sublist]
#         return flattened_results

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


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


# def get_posts(db: Session):
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


def get_my_post(db: Session, 
                limit: int, 
                skip: int, 
                search: Optional[str], 
                current_user):
    
    posts = db.query(models.Post).filter(models.Post.title.contains(search), 
                                         models.Post.user_id == current_user.id).limit(limit).offset(skip).all()

    return posts


def get_post_in_group(group_id: int, 
                      db: Session,
                      current_user):
    
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found group with {id}!")
    
    member = db.query(models.Member).filter(models.Member.group_id == group_id, 
                                            models.Member.user_id == current_user.id, 
                                            models.Member.status == "accepted")
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not in this group!")

    # posts = db.query(models.Post).filter(models.Post.group_id == group_id, 
    #                                      models.Post.status == "accepted").all()
    
    # posts = db.query(models.Post, func.count(models.Vote.post_id).label('vote'))
    # posts = posts.join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    # posts = posts.filter(models.Post.group_id == group_id, 
    #                      models.Post.status == "accepted").all()
    
    posts = db.query(models.Post, 
                     func.count(models.Vote.post_id).label('Vote'), 
                     func.count(models.Comment.post_id).label('Comment'))
    posts = posts.join(models.Vote, 
                       models.Post.id == models.Vote.post_id,
                       isouter=True)
    posts = posts.join(models.Comment, 
                       models.Post.id == models.Comment.post_id,
                       isouter=True)
    posts = posts.group_by(models.Post.id)
    posts = posts.filter(models.Post.group_id == group_id, 
                         models.Post.status == "accepted").all()
    
    return posts


def create_post(post_create: schemas.PostCreate, 
                db: Session, 
                current_user):
    
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


def handle_post(post_status: schemas.PostHandle, 
                db: Session, 
                current_user):
    
    post_query = db.query(models.Post).filter(models.Post.id == post_status.id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Not found post!")

    admin = db.query(models.Member).filter(models.Member.group_id == post.group_id,
                                           models.Member.user_id == current_user.id, 
                                           models.Member.role == "admin")
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= "Only admin can handle member!")
    
    post_query.update({models.Member.status: post_status.status}, synchronize_session=False)
    db.commit() 
    
    return post_query.first()


def delete_post(post_id: int, 
                db: Session, 
                current_user):
    
    post_query = db.query(models.Post).filter(models.Post.id == post_id, 
                                              models.Post.status == "accepted")
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {post_id}!")
        
    admin = db.query(models.Member).filter(models.Member.id == current_user.id, 
                                           models.Member.group_id == post.group_id, 
                                           models.Member.role == "admin").first()    
    if (not admin) and post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not permission!")
    post_query.update({"status": "deleted"}, 
                      synchronize_session=False)
    db.commit()
    return {"message": "Succes!"}


def update_post(post_id: int, 
                newPost: schemas.PostUpdate, 
                db: Session, 
                current_user):
    
    post_query = db.query(models.Post).filter(models.Post.id == post_id, 
                                              models.Post.status == "accepted")
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {post_id}!")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not alowwed post with {post_id}!")
    post_query.update(newPost.dict(), synchronize_session=False)
    db.commit()
    
    return post


async def upload_file(file: UploadFile,
                      db: Session, 
                      current_user):

    UPLOAD_DIRECTORY = os.path.abspath("./files/")
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    new_file = models.File(path=file_location, 
                           user_id=current_user.id, 
                           name=file.filename)
    db.add(new_file)
    db.commit()

    return {"filename": file.filename, 
            "status": "accepted!"}


def download_file(db: Session = Depends(get_db), 
                  current_user = Depends(oauth2.get_current_user)):

    file = db.query(models.File).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Not found!")
    
    return FileResponse(file.path)