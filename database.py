from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Format: postgresql://user:password@localhost/db_name
URL = "postgresql://postgres:postgres@localhost/cars_db"
engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# This is a 'Dependency' we'll use in our routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()