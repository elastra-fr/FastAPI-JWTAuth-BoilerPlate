from .auth import get_current_user
from database import SessionLocal
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated


# Create the router with the prefix /user
router = APIRouter(
    prefix="/user",
    tags=["user"]
)


# Get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define the dependencies
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create the request model

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


# Read current user informations
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return db.query(Users).filter(Users.id == user.get("id")).first()


# Update user password

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(
            status_code=401, detail="Error: Incorrect password")

    user_model.hashed_password = bcrypt_context.hash(
        user_verification.new_password)

    db.add(user_model)
    db.commit()
