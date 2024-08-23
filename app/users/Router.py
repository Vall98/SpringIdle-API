from app.users import controller
from app.users.db import User
from app.users.scopes import Scopes, RouteScopes
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter(prefix="/users")

@router.get('/')
def get_home_page():
    return {"Hello": "World", "status": 200}

@router.post('/create')
def signup(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = controller.create_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username already taken",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": controller.create_access_token(user), "token_type": "bearer"}

@router.post('/token')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = controller.get_user(form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": controller.create_access_token(user), "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: Annotated[User, Security(controller.get_current_user, scopes=[Scopes.USER_ME])]):
    return current_user

@router.get("/all")
async def get_all_users(users: Annotated[User, Security(controller.get_all_users, scopes=[Scopes.USER_READ_ALL])]):
    return users