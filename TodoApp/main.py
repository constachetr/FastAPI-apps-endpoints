from fastapi import FastAPI  # Importing the FastAPI class to create an API instance
import models  # Importing the database models defined in the project
from database import engine  # Importing the database engine to connect to the database
from routers import auth, todos, admin, users  # Importing router modules for different API functionalities

# Create a FastAPI application instance
app = FastAPI()

# Create all database tables defined in the models module
models.Base.metadata.create_all(bind=engine)
# `metadata.create_all` uses the SQLAlchemy engine to create the database tables if they don't already exist.

# Include the authentication router
app.include_router(auth.router)
# Adds all the routes defined in `auth.router` to the FastAPI app.

# Include the todos router
app.include_router(todos.router)
# Adds all the routes defined in `todos.router` to the FastAPI app.

# Include the admin router
app.include_router(admin.router)
# Adds all the routes defined in `admin.router` to the FastAPI app.

# Include the users router
app.include_router(users.router)
# Adds all the routes defined in `users.router` to the FastAPI app.
