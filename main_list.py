from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()

# Constraints of Posts: VALIDATION of types
class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    rating: Optional[int] = None

my_posts = []

#Main route
@app.get("/")
async def root():
    return {"message": "Hello World"}

#Get all posts
@app.get("/posts")
def get_posts():
    return {"data": my_posts}

#Post a new post
@app.post("/posts",status_code = status.HTTP_201_CREATED,) 
async def create_posts(post: Post = Body(...)):
    post_dict = post.dict()
    post_dict["id"] = randrange(0,100000)
    my_posts.append(post_dict)
    print(f"Post created with title as {post.title} and content as {post.content}")
    return {"data": post_dict}

#Get Latest Post
@app.get("/posts/latest")
async def get_latest_post():
    return my_posts[-1] if len(my_posts) > 0 else None

def find_post(id: int):
    for post in my_posts:
        if post["id"] == id:
            return post
    return None

#Get a single post(FIND)
@app.get("/posts/{id}", status_code = status.HTTP_302_FOUND)
async def get_post(id: int, response: Response):
   
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    # if not post: MEANS post is empty
    # response.status_code = status.HTTP_404_NOT_FOUND #Error 404 item is not found
    # return {"message": f"Post with id {id} not found"}
    return {"data": post}


#Delete Post
@app.delete("/posts/{id}")
def delete_post(id: int, status_code = status.HTTP_204_NO_CONTENT):
    post = find_post(id)
    if not post: #if post == None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    my_posts.remove(post)
    return {"data": f"Post with id {id} is deleted"}

#Update Post
@app.put("/posts/{id}", status_code = status.HTTP_202_ACCEPTED)
def update_post(id: int, post: Post):
    post_dict = post.dict()
    post_dict["id"] = id
    post_to_update = find_post(id)
    if not post_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    my_posts.remove(post_to_update)
    my_posts.append(post_dict)
    return {"data": post_dict}