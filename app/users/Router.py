from app.users import Controller
from app.users.db import User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(prefix="/users")

@router.get('/')
def get_home_page():
    return {"Hello": "World", "status": 200}

@router.post('/create')
def signup(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Controller.create_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username already taken",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": Controller.create_access_token(form_data.username), "token_type": "bearer"}

@router.post('/token')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Controller.get_user(form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": Controller.create_access_token(form_data.username), "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: Annotated[User, Depends(Controller.get_current_user)]):
    return current_user