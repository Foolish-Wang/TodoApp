from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Defining the database URL
SQLALCHEMY_DATABASE_URL = os.getenv("AIVEN_PASSWORD")

# Creating a database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creating a session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creating a base class
Base = declarative_base()
