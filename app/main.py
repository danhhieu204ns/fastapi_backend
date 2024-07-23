import time
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastApi', user='postgres', password='1003', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database succesfull!!")
#         break
#     except Exception as error:
#         print("Database faled!")
#         print("Error: ", error)
#         time.sleep(4)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
async def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/post")
async def getPosts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/post/{id}")
async def getPost(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return post

@app.post("/post", status_code=status.HTTP_201_CREATED)
async def createPost(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING * """,
    #                (post.title, post.content))
    # newPost = cursor.fetchone()
    # conn.commit()
    newPost = models.Post(**post.dict())
    db.add(newPost)
    db.commit()
    db.refresh(newPost)
    return {"message": newPost}

@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Succes!"}

@app.put("/post/{id}")
async def updatePost(id: int, newPost: Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts 
    #                SET title = %s, content = %s 
    #                WHERE id = %s 
    #                RETURNING *""", 
    #                (newPost.title, newPost.content, str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    post.update(newPost.dict(), synchronize_session=False)
    db.commit()
    return {"message": post.first()}
