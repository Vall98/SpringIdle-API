import app_secrets
import bcrypt
import jwt

from app.users.db import user_table
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(username : str):
    data = {"sub": username}
    expires_delta = timedelta(minutes=app_secrets.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app_secrets.SECRET_KEY, algorithm=app_secrets.ALGORITHM)
    return encoded_jwt

def hash_password(password : str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(plain : str, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    cred_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, app_secrets.SECRET_KEY, algorithms=[app_secrets.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise cred_error
    except InvalidTokenError:
        raise cred_error
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
