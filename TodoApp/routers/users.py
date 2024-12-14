from typing import Annotated  # Importing Annotated for type hinting dependencies
from pydantic import BaseModel, Field  # Importing BaseModel for request validation and Field for field validation
from sqlalchemy.orm import Session  # Importing Session to interact with the database
from fastapi import APIRouter, Depends, HTTPException, Path  # Importing FastAPI utilities for routing, dependency injection, and exception handling
from starlette import status  # Importing HTTP status codes
from models import Todos, Users  # Importing the Todos and Users models for database operations
from database import SessionLocal  # Importing the session factory for database connections
from .auth import get_current_user  # Importing the authentication function to get the current user
from passlib.context import CryptContext  # Importing CryptContext for password hashing

# Create an API router for user-related endpoints
router = APIRouter(
    prefix='/users',  # All routes under this router will have the /users prefix
    tags=['users']  # Tagging these routes for documentation purposes
)

# Dependency to provide a database session
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Yield the session for use in route handlers
    finally:
        db.close()  # Ensure the session is closed after use

# Dependency annotations for type hinting
db_dependency = Annotated[Session, Depends(get_db)]  # Dependency to inject the database session
user_dependency = Annotated[dict, Depends(get_current_user)]  # Dependency to inject the current authenticated user

# Creating a password hashing context with bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Pydantic model for password change request validation
class UserVerification(BaseModel):
    password: str  # Current password to be verified
    new_password: str = Field(min_length=6)  # New password with a minimum length of 6 characters

# Route to get user details
@router.get("/", status_code=status.HTTP_200_OK)  # HTTP GET route at /users/
async def get_user_details(user: user_dependency, db: db_dependency):
    if user is None:  # Check if the user is authenticated
        raise HTTPException(status_code=401, detail='Authentication failed')  # Raise error if not authenticated
    return db.query(Users).filter(Users.id == user.get('id')).first()  # Fetch and return the user from the database

# Route to change user password
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)  # HTTP PUT route at /users/password
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):  # Accept user details and password change request
    if user is None:  # Check if the user is authenticated
        raise HTTPException(status_code=401, detail='Authentication Failed')  # Raise error if not authenticated
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()  # Fetch the user model from the database

    # Verify if the provided password matches the stored hashed password
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_pass):
        raise HTTPException(status_code=401, detail='Error on changing the password')  # Raise error on mismatch

    # Hash the new password and update the user's password in the database
    user_model.hashed_pass = bcrypt_context.hash(user_verification.new_password)

    db.add(user_model)  # Add the updated user model to the session
    db.commit()  # Commit the changes to the database

