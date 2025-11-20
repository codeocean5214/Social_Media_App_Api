from collections.abc  import AsyncGenerator 
import uuid 
from sqlalchemy import Column,String,Text,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.ext.asyncio import  AsyncSession, create_async_engine,async_sessionmaker 
from fastapi import Depends,    requests
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, relationship 
from fastapi_users.db import SQLAlchemyUserDatabase,SQLAlchemyBaseUserTableUUID


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
#data moodel
class Base(DeclarativeBase):
    pass

#defining thw user model and the user class for the auth part we are using jwt
class User(Base,SQLAlchemyBaseUserTableUUID) : 
    posts = relationship("Post",back_populates="user")
#one to many relationship 

class Post(Base) : 
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4 )
    user_id = Column(UUID(as_uuid=True),ForeignKey("user.id"),nullable=False)
    caption = Column(Text)
    url =Column(String,nullable=False)
    file_type  =Column(String,nullable=False)
    file_name =Column(String,nullable=False)
    time_created = Column(DateTime,default=datetime.utcnow)

    #creating a realtionship
    user = relationship("User",back_populates="posts")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine,expire_on_commit=False)

#asynchronous function to create tables and store data in the database file
async def create_table_db():
    async with engine.begin() as conn : #starts the asynchronus connection and waits for it
        await conn.run_sync(Base.metadata.create_all)

#start the session 
async def get_async_session()-> AsyncGenerator[AsyncSession,None] : 
    async with async_session_maker() as session : 
        yield session 
#USER databse table getter  
async def get_user_db(
        session : AsyncSession = Depends(get_async_session)
        ) : 
    yield SQLAlchemyUserDatabase(session,User)

