from sqlalchemy import create_engine  # Import for creating a connection to the database
from sqlalchemy.orm import sessionmaker  # Import for managing database sessions
from sqlalchemy.ext.declarative import declarative_base  # Import for creating the base class for models

# Define the database URL for an SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# The path "./todos.db" means the SQLite database file will be created or accessed in the current directory.

# Create a database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite to allow multiple threads to access the database
)

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,  # Disable autocommit; transactions must be explicitly committed
    autoflush=False,  # Disable autoflush; changes are not automatically flushed to the database
    bind=engine  # Bind the sessionmaker to the database engine
)

# Create a base class for models
Base = declarative_base()
# This Base class will be inherited by all ORM models to define database tables.

