from .auth import get_current_user
from database import SessionLocal
from fastapi import APIRouter, Depends, Path
from fastapi.exceptions import HTTPException
from models import Todo
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated


# Create the router with the prefix /admin
router = APIRouter(
    prefix="/admin",
    tags=["admin"]
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

# Read all todo items - Only admin users can access this route


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

       if user is None or user.get("role") != "admin":
            raise HTTPException(
                status_code=401, detail="User not authenticated")

       return db.query(Todo).all()

# Delete a single todo item by id - Only admin users can access this route

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

       if user is None or user.get("role") != "admin":
            raise HTTPException(status_code=401, detail="User not authenticated")

       todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
        
       if todo_model is None:
            raise HTTPException(status_code=404, detail="Todo item not found")

       db.query(Todo).filter(Todo.id == todo_id).delete()
       db.commit()
