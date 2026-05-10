from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./hardloop.db" #  Creates a file called hardloop.db in the current directory

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)  # Talks to the database

SessionLocal = sessionmaker(bind=engine) # A temporary connection every time you use DB

Base = declarative_base() # Parent class for all our models, it helps SQLAlchemy to understand how to create tables and manage data.


