from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time 

app = FastAPI()

# Constraints of Posts: VALIDATION of types
class Post(BaseModel):
    title: str
    content: str
    published: bool = False
    #rating: Optional[int] = None
    #created date ON postgreSQL

#Database connection
while True:
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "8520",
                                    host = 'localhost',
                                    database= 'db',
                                    port = '5432',
                                    cursor_factory=RealDictCursor
                                    )
        cursor = connection.cursor()
        print(f"\033[92mPostgreSQL connection is successful \033[0m")
        break
    except (Exception, psycopg2.Error) as error:
        print(f"\033[91mError while connecting to PostgreSQL\n{error}\033[0m")
        time.sleep(3)

        
def check_if_table_exists():
    schema_name="public"
    table_name="posts"

    Check_query ="""SELECT EXISTS (
                    SELECT FROM pg_catalog.pg_class c
                    JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    WHERE  n.nspname = '%s'
                    AND    c.relname = '%s'
                    AND    c.relkind = 'r'    -- only tables
                    )""" % (schema_name,table_name)
    cursor.execute(Check_query)

    return cursor.fetchone()['exists']


#Main route
@app.get("/")
async def root():
    return {"message": "Hello World"}


#Get all posts
@app.get("/posts")
def get_posts():
    ### first check if table exists
    if not check_if_table_exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, content="Table does not exist")
    
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

#Create a new post
@app.post("/posts",status_code = status.HTTP_201_CREATED,) 
async def create_posts(post: Post = Body(...)):
    if not check_if_table_exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, content="Table does not exist")

    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    posts = cursor.fetchone()

    connection.commit()

    return {"data": posts}

#Get Latest Post
# @app.get("/posts/latest")
# async def get_latest_post():
#     return my_posts[-1] if len(my_posts) > 0 else None

#Get a single post(FIND)
@app.get("/posts/{id}", status_code = status.HTTP_302_FOUND)
async def get_post(id: int):

    if not check_if_table_exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, content="Table does not exist")  # type: ignore

    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),)) # neden , var bilmiyorum
    posts = cursor.fetchone()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    return {"data": posts}

#Delete Post
@app.delete("/posts/{id}")
def delete_post(id: int, status_code = status.HTTP_204_NO_CONTENT):

    if not check_if_table_exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, content="Table does not exist")  # type: ignore

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),)) # neden , var bilmiyorum
    posts = cursor.fetchone()
    if not posts: #if post == None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    
    connection.commit()

    return {"data": f"Post with id {id} is deleted"}

# #Update Post
# @app.put("/posts/{id}", status_code = status.HTTP_202_ACCEPTED)
# def update_post(id: int, post: Post):
#     post_dict = post.dict()
#     post_dict["id"] = id
#     post_to_update = find_post(id)
#     if not post_to_update:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
#     my_posts.remove(post_to_update)
#     my_posts.append(post_dict)
#     return {"data": post_dict}