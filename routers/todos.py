from fastapi import APIRouter, Path, HTTPException, Depends, Request
from starlette import status
from pydantic import BaseModel, Field
from models import Todos
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/todos',
    tags=['todos']
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


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ###
@router.get("/todo-page")
async def render_todo_page(request:Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.owner_id==user.get("id")).all()
        return templates.TemplateResponse('todos.html', {'request':request, 'todos':todos,'user':user})
    except:
        redirect_to_login()

@router.get('/add-todo-page')
async def render_add_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None :
            return redirect_to_login()
        
        return templates.TemplateResponse("add-todo.html",{'request':request,'user':user})
    except:
        return redirect_to_login()

@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request:Request, todo_id:int, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None :
            return redirect_to_login()
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html",{'request':request,'todo':todo, "user":user})
    except:
        return redirect_to_login()


### EndPoints ###
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
async def update_todo(user:user_dependency,
                      db:db_dependency,
                      todo_id:int,
                      todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed..')
    todo_model = db.query(Todos).filter(Todos.id==todo_id)\
        .filter(Todos.owner_id==user.get('id')).first()
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
async def delete_todo(user:user_dependency,
                      db:db_dependency,
                      todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed..')
    todo_model = db.query(Todos).filter(Todos.id==todo_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo is not found...")
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()