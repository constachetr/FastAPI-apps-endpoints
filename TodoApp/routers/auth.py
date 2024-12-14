from typing import Annotated

from sqlalchemy.orm import Session  # For database session management
from starlette import status  # HTTP status codes
from database import SessionLocal  # Database session factory
from models import Users  # Database model for user entities
from passlib.context import CryptContext  # For password hashing
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # OAuth2 authentication
from jose import jwt, JWTError  # For generating and verifying JWTs
from fastapi import APIRouter, Depends, HTTPException  # FastAPI tools for building APIs
from datetime import datetime, timedelta, timezone  # For managing expiration of tokens
from pydantic import BaseModel  # Data validation and parsing

# Create a FastAPI router for authentication-related routes
router = APIRouter(
    prefix='/auth',  # All routes will start with '/auth'
    tags=['auth']  # Group under 'auth' tag in the documentation
)

# Secret key and algorithm for JWT encoding and decoding
SECRET_KEY = '12fdfd2f1d2fd2fd2f2df2df21d21sf21r2wf1t21t12g12f12df1d2f1d2f1sd2f1d2'
ALGORITHM = 'HS256'

# Password hashing context using bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# OAuth2 scheme to handle bearer tokens
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Pydantic model to handle user creation requests
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

# Pydantic model to represent the structure of a returned token
class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated dependency for database sessions
db_dependency = Annotated[Session, Depends(get_db)]

# Function to authenticate a user
def authentificate_user(username: str, password: str, db):
    # Query the user by username
    user = db.query(Users).filter(Users.username == username).first()
    # If user not found or password doesn't match, return False
    if not user or not bcrypt_context.verify(password, user.hashed_pass):
        return False
    return user  # Return the user object if authentication is successful

# Function to create an access token
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    # Payload for the token
    encode = {'sub': username, 'id': user_id, 'role': role}
    # Add expiration time to the payload
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    # Encode the payload into a JWT
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to extract and validate the current user from the token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        # If essential fields are missing, raise an exception
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user')
        # Return user details
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        # If decoding fails, raise an exception
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')

# Route to create a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # Create a user model instance from the request
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_pass=bcrypt_context.hash(create_user_request.password),  # Hash the password
        is_active=True  # Set the user as active by default
    )
    db.add(create_user_model)  # Add the new user to the session
    db.commit()  # Commit the session to save changes

# Route to generate a token for a user
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Authenticate the user using their username and password
    user = authentificate_user(form_data.username, form_data.password, db)
    if not user:
        # If authentication fails, raise an exception
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')
    # Create an access token valid for 20 minutes
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    # Return the token and its type
    return {'access_token': token, 'token_type': 'bearer'}


