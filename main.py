from fastapi import FastAPI, Depends, HTTPException, Path
import models
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

# pydantic model for todo request
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

# fetching all todos : endpoint
@app.get("/",status_code=status.HTTP_200_OK)
async def fetch_all(db: db_dependency):
    return db.query(Todos).all()

# fetching todo by id : endpoint
@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def fetch_todo_by_id(db:db_dependency,todo_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found...')

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependency,
                      todo_request:TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()