from typing import Annotated  # Used for type annotations
from pydantic import BaseModel, Field  # For request validation and field constraints
from sqlalchemy.orm import Session  # For database session handling
from fastapi import APIRouter, Depends, HTTPException, Path  # FastAPI components for routing and exception handling
from starlette import status  # For HTTP status codes
from models import Todos  # Database model for the Todos entity
from database import SessionLocal  # Database session factory
from .auth import get_current_user  # Function to get the authenticated user

# Create a FastAPI router for organizing endpoints
router = APIRouter()

# Dependency to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated dependencies for database session and authenticated user
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Pydantic model for validating and structuring Todo requests
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)  # Title must be at least 3 characters
    description: str = Field(min_length=3, max_length=100)  # Description length between 3 and 100
    priority: int = Field(gt=0, lt=10)  # Priority must be between 1 and 9
    complete: bool  # Boolean field for completion status

# Endpoint to fetch all todos of the authenticated user
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        # If user is not authenticated, raise 401 Unauthorized
        raise HTTPException(status_code=401, detail='Authentification Failed')
    # Query todos owned by the user
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

# Endpoint to fetch a specific todo by ID for the authenticated user
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification Failed')

    # Query the specific todo owned by the user
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    # If the todo is not found, raise 404 Not Found
    raise HTTPException(status_code=404, detail='Todo found.')

# Endpoint to create a new todo for the authenticated user
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification Failed')
    # Create a new todo using the request data and owner's ID
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))

    db.add(todo_model)  # Add the todo to the database session
    db.commit()  # Commit the session to save changes

# Endpoint to update an existing todo
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification Failed')

    # Query the todo to update
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    # Update fields of the todo
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)  # Add updated todo to the session
    db.commit()  # Commit changes to save

# Endpoint to delete a specific todo
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification Failed')

    # Query the todo to delete
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    # Delete the todo
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()  # Commit changes to save

