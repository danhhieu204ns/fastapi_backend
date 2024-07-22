import time
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastApi', user='postgres', password='1003', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database succesfull!!")
        break
    except Exception as error:
        print("Database faled!")
        print("Error: ", error)
        time.sleep(4)
    
myPosts = [
    
]

def findPost(postList, id):
    for post in postList:
        if id == post['id']:
            return post
    return

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/post")
async def getPosts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

@app.post("/post", status_code=status.HTTP_201_CREATED)
async def createPost(post: Post):
    cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING * """,
                   (post.title, post.content))
    newPost = cursor.fetchone()
    conn.commit()
    return {"message": newPost}

@app.get("/post/{id}")
async def getPost(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return post

@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return {"message": "Succes!"}

@app.put("/post/{id}")
async def updatePost(id: int, newPost: Post):
    cursor.execute("""UPDATE posts 
                   SET title = %s, content = %s 
                   WHERE id = %s 
                   RETURNING *""", 
                   (newPost.title, newPost.content, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    return {"message": "Succes!"}
