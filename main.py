from fastapi import FastAPI, Request, status
import models
from database import engine
from routers import admin, auth, todos, users

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
async def welcome(request:Request):
    return RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)