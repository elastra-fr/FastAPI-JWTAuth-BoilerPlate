from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os



# Load the environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")



SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create the database engine using the URL and connect_args to avoid threading issues
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
 #                      "check_same_thread": False})

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a sessionmaker object to create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the database models

Base = declarative_base()
