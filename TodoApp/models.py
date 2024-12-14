from database import Base  # Import the Base class from the database module to create models
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # Import types and constraints for database columns

class Users(Base):  # Define a database model named 'Users'
    __tablename__ = 'users'  # Specify the table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Primary key column, indexed for quick lookup
    email = Column(String, unique=True)  # Email column, values must be unique
    username = Column(String, unique=True)  # Username column, values must be unique
    first_name = Column(String)  # Column to store the user's first name
    last_name = Column(String)  # Column to store the user's last name
    hashed_pass = Column(String)  # Column to store the hashed password
    is_active = Column(Boolean, default=True)  # Boolean column, defaults to True for active users
    role = Column(String)  # Role column to define the user's role (e.g., admin, user)


class Todos(Base):  # Define a database model named 'Todos'
    __tablename__ = 'todos'  # Specify the table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Primary key column, indexed for quick lookup
    title = Column(String)  # Column to store the title of the todo
    description = Column(String)  # Column to store a description of the todo
    priority = Column(Integer)  # Column to store the priority level as an integer
    complete = Column(Boolean, default=False)  # Boolean column, defaults to False for incomplete todos
    owner_id = Column(Integer, ForeignKey("users.id"))
    # Foreign key linking the todo to a specific user by referencing the 'id' column in the 'users' table
