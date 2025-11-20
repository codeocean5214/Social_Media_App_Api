from fastapi import FastAPI,Path ,HTTPException ,File,UploadFile,Form,Depends
import uvicorn as uv
from images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from schema import CreatePost , UserCreate , UserRead
from sqlalchemy import select 
from db import Post,create_table_db,get_async_session 
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager 
from sqlalchemy.exc import SQLAlchemyError 
import shutil
import os  
import tempfile
import uuid  
from users import auth_backend,current_active_user,fastapi_users
@asynccontextmanager 
async def db_conn(app : FastAPI): 
    await create_table_db()
    yield 

app=FastAPI(lifespan=db_conn)
app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt",tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix="/auth",tags=["auth"])
#app.include_router(fastapi_users.get_users_router(UserRead),prefix="/users",tags=["users"])


"""
url = "https://file-examples.com/wp-content/uploads/2017/10/file_example_JPG_100kB.jpg"
upload = imagekit.upload_file(
        file=url,
        file_name="test-url.jpg",
        options=UploadFileRequestOptions(
            response_fields=["is_private_file", "tags"],
            tags=["tag1", "tag2"]
        )
    )
"""

@app.post('/upload') 
async def upload_file(
    file : UploadFile  = File(...), 
    caption : str = Form(""), 
    session : AsyncSession = Depends(get_async_session) #dependency injection
    ): 
    temp_path = None
    try : 
        with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(file.filename)[1]) as temp_file : 
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        upload_result = imagekit.upload_file(
             file=open(temp_path,"rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
            use_unique_file_name=True,
            tags=["backend-upload"]
        )   
        )
        status = None
        try:
            status = upload_result.response_metadata.http_status_code
        except Exception:
            status = None
        if status==200 : 
            post= Post(
            caption= caption,
            url = upload_result.url, 
            file_type="photo" if file.content_type.startswith("image/") else "video", 
            file_name = upload_result.name 
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

        
        raise HTTPException(status_code=500, detail="upload failed")
                
    except Exception as e  : 
            raise HTTPException(status_code=404 , detail=f"error : {e}")
    finally : 
        if temp_path and os.path.exists(temp_path):
            try  :   
                os.unlink(temp_path)
            except : 
                pass
        try : 
            file.file.close()
        except  Exception : 
            pass
    
            
    """    session.add(post)
    await session.commit()
    await session.refresh(post)"""

@app.get("/feed") 
async def get_feed(
    session : AsyncSession = Depends(get_async_session)
): 
    res = await session.execute(select(Post).order_by(Post.time_created.desc()))
    #we are simply executing  Select * from Post order by date desc  
    #the fastapi returns data in cursor objects so in order to fetch the data we use 
    #convert the obj into list
    # data is returned in something like this  : [(1,), (2,), (3,)] so thats why row[0]
    feed = [row[0] for row in res.all()]
    post_data = []
    for post in feed : 
        post_data.append(
            {
                "id" : str(post.id),
                "caption" : post.caption, 
                "file_type" : post.file_type,
                "file_name" : post.file_name,
                "time_created" : post.time_created.isoformat()
            }
        )
    return {'Posts' : post_data }


@app.delete("/posts/{post_id}")
async def delete_post(post_id : str, session : AsyncSession = Depends(get_async_session)) : 
    try : 
        post_uuid = uuid.UUID(post_id) 
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if post == None : 
            raise HTTPException(status_code=404,detail="No post found")
        await session.delete(post)
        await session.commit()

        return {'m' : 'The post is deleted'}
    except Exception as e : 
        raise HTTPException(status_code=404,detail=str(e))


#basic end point  
#filler data 

"""text_posts = {
    "1": {
        "title": "New Post",
        "content": "cool test post"
    },
    "2": {
        "title": "Second Post",
        "content": "another awesome post for testing"
    },
    "3": {
        "title": "FastAPI Tutorial",
        "content": "learning how to create APIs with FastAPI"
    },
    "4": {
        "title": "Tech News Update",
        "content": "Python 3.13 brings major performance improvements!"
    },
    "5": {
        "title": "Daily Motivation",
        "content": "Success is built on consistency, not intensity."
    },
    "6": {
        "title": "My Coding Journey",
        "content": "Started learning FastAPI today, and it's amazing!"
    }
}

#get all the post
@app.get("/post")
async def get_all_posts(limit: int = None):
    if limit : 
        return list(text_posts.values())[:limit]
    if limit is None : 
        return text_posts 
#getting the post by id we use params or path parameter 

@app.get('/post/{id}')
async def get_post_by_id(id:int) ->CreatePost: 
    if str(id) not in text_posts: 
        raise HTTPException(status_code=404,detail="Post Not Found")
    return text_posts.get(str(id))
#data return is either pydantic object or dict 
@app.post("/create_post")
async def create_post(post: CreatePost) -> CreatePost : 
    new_post = {'title' : post.title ,'content':post.content} 
    new_id = str(max(map(int, text_posts.keys()), default=0) + 1)
    text_posts[new_id] = new_post 
    return new_post
"""

if __name__ =="__main__": 
    uv.run("app:app",host="127.0.0.1",port=9999,reload=True)