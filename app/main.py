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
    newPost = post.model_dump()
    newPost['id'] = randrange(0, int(1e9))
    myPosts.append(newPost)
    print(myPosts)
    return {"message": "Succes!"}

@app.get("/post/{id}")
async def getPost(id: int):
    post = findPost(myPosts, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Not found post with {id}!"}
    print(post)
    return post

@app.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletePost(id: int):
    post = findPost(myPosts, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found post with {id}!")
    myPosts.remove(post)
    return {"message": "Succes!"}

@app.put("/post/{id}")
async def updatePost(id: int, newPost: Post):
    for post in myPosts:
        if id == post['id']:
            post = newPost
            return {"message": "Succes!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Not found post with {id}!")