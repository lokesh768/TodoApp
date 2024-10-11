from fastapi import APIRouter, Path, HTTPException, Depends
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix = '/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def fetch_all(user:user_dependency,
                    db:db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed..')
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,
                      db:db_dependency,
                      todo_id:int=Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication failed..')
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found...")
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()