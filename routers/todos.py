from fastapi import APIRouter, Path, HTTPException, Depends
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    tags=['Todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# pydantic model for todo request
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

# fetching all todos : endpoint
@router.get("/",status_code=status.HTTP_200_OK)
async def fetch_all(user:user_dependency,
                    db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed..')
    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()

# fetching todo by id : endpoint
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def fetch_todo_by_id(user:user_dependency,
                           db:db_dependency,
                           todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed..')
    todo_model = db.query(Todos).filter(Todos.id==todo_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found...')

# creating todo : endpoint
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,
                      db:db_dependency,
                      todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed..')
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

# updating todo : endpoint
@router.put("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,
                      todo_id:int,
                      todo_request:TodoRequest):
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is  None:
        raise HTTPException(status_code=404, detail="Todo Not Found...")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()

# deleting a todo : endpoint
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency,
                      todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found...")
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()