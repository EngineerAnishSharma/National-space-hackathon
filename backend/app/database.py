# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

DATABASE_URL = "sqlite:///./iss_cargo.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    itemId = Column(String, primary_key=True, index=True)
    name = Column(String)
    width = Column(Float)
    depth = Column(Float)
    height = Column(Float)
    mass = Column(Float)
    priority = Column(Integer)
    expiryDate = Column(Date, nullable=True)  # Remove typing.Optional
    usageLimit = Column(Integer, nullable=True) # Remove typing.Optional
    preferredZone = Column(String)

class Container(Base):
    __tablename__ = "containers"

    containerId = Column(String, primary_key=True, index=True)
    zone = Column(String)
    width = Column(Float)
    depth = Column(Float)
    height = Column(Float)

class Placement(Base):
    __tablename__ = "placements"

    id = Column(Integer, primary_key=True, index=True)
    itemId = Column(String)
    containerId = Column(String)
    start_w = Column(Float)
    start_d = Column(Float)
    start_h = Column(Float)
    end_w = Column(Float)
    end_d = Column(Float)
    end_h = Column(Float)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()