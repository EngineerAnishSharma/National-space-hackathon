# /app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import Config

# Create the SQLAlchemy engine
engine = create_engine(Config.DATABASE_URL) # Add connect_args={"check_same_thread": False} for SQLite

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a thread-local Session proxy
# This helps manage sessions in a web application context
db_session = scoped_session(SessionLocal)

# Create a Base class for declarative class definitions
Base = declarative_base()
Base.query = db_session.query_property() # Optional: Adds convenient Base.query access

def init_db():
    """Initializes the database and creates tables."""
    # Import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import app.models_db # noqa
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

def get_db():
    """Dependency function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# You might also want a way to tear down the session context
# in a web framework like Flask, often done after each request.
# Flask-SQLAlchemy handles this, but with manual setup:
# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()