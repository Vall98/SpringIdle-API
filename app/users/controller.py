from app.users.auth import check_password, hash_password, RouteCredentials
from app.users.db import user_table
from fastapi import HTTPException, Security, status
from typing import Annotated

def get_current_user(username: Annotated[str, Security(RouteCredentials)]):
    cred_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user(username)
    if user is None:
        raise cred_error
    return user

def get_user(username, password=None):
    user = user_table.get_user(username, include_pwd=(password is not None))
    if user and password and not check_password(password, user.password):
        return None
    return user

def create_user(username, password):
    return user_table.add_user(username, hash_password(password))

def get_all_users(_: Annotated[str, Security(RouteCredentials)]):
    return user_table.get_users()