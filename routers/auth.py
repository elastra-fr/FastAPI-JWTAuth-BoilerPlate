from database import SessionLocal
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated
import os

# Create the router with the prefix /auth
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Load the environment variables
load_dotenv()

# Get the secret key and algorithm
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Create the password context
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# Create the request models


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class JSONLoginRequest(BaseModel):
    username: str
    password: str

# Create the response model


class Token(BaseModel):
    access_token: str
    token_type: str

# Get the database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define the dependencies
db_dependency = Annotated[Session, Depends(get_db)]

# Authenticate a user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()

    # Check if the user exists
    if not user:
        return False

    # Check if the password is correct
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    # Return the user if the user exists and the password is correct
    return user

# Create an access token


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Get the current user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")

        return {"username": username, "id": user_id, "role": user_role}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")


# Create a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer"}

# Route pour l'authentification via JSON
@router.post("/json-token", response_model=Token)
async def login_with_json(json_request: JSONLoginRequest, db: db_dependency):
    user = authenticate_user(db, json_request.username, json_request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer"}