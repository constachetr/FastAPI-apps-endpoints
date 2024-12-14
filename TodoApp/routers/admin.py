from typing import Annotated  # Annotated allows combining metadata with type hints
from pydantic import BaseModel, Field  # For data validation and parsing in request bodies
from sqlalchemy.orm import Session  # SQLAlchemy session for database interaction
from fastapi import APIRouter, Depends, HTTPException, Path  # FastAPI utilities for building APIs
from starlette import status  # HTTP status codes for response standards
from models import Todos  # Importing the Todos model for database operations
from database import SessionLocal  # Importing the database session factory
from .auth import get_current_user  # Dependency to get the currently authenticated user

# Define a router for the admin-related routes
router = APIRouter(
    prefix='/admin',  # All routes will start with '/admin'
    tags=['admin']  # Routes will be grouped under the 'admin' tag in API docs
)

# Dependency to provide a database session
def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Provide the session to the route handlers
    finally:
        db.close()  # Ensure the session is closed after use

# Dependency to inject the database session
db_dependency = Annotated[Session, Depends(get_db)]
# Dependency to inject the current user from the authentication system
user_dependency = Annotated[dict, Depends(get_current_user)]

# Route to read all todos (admin access required)
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    # Check if the user is authenticated and has admin privileges
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Query the database for all todos and return the result
    return db.query(Todos).all()

# Route to delete a specific todo by ID (admin access required)
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # Validate if the user is authenticated and has admin privileges
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Query the database to find the todo with the given ID
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    # If the todo does not exist, raise a 404 error
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    # Delete the todo from the database
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()  # Commit the transaction to save changes
