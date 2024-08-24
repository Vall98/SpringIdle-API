import app_secrets
import bcrypt
import jwt

from app.users.db import User
from app.users.scopes import Roles, scopes
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token", scopes=scopes[Roles.ALL])

class TokenAttributes(StrEnum):
    USERNAME = "sub"
    SCOPES = "scopes"
    EXPIRES = "exp"

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(plain: str, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed)

def create_access_token(user: User):
    data = {TokenAttributes.USERNAME: user.username, TokenAttributes.SCOPES: scopes[user.perm_level]}
    expires_delta = timedelta(minutes=app_secrets.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({TokenAttributes.EXPIRES: expire})
    encoded_jwt = jwt.encode(to_encode, app_secrets.SECRET_KEY, algorithm=app_secrets.ALGORITHM)
    return encoded_jwt, expire

def _check_scopes(route_scopes, user_scopes):
    if route_scopes and user_scopes:
        for scope in route_scopes:
            if scope not in user_scopes:
                return False
        return True
    elif route_scopes:
        return False
    else:
        return True

def RouteCredentials(route_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired, please refresh your credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    perm_level_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, app_secrets.SECRET_KEY, algorithms=[app_secrets.ALGORITHM])
    
    username: str | None = payload.get(TokenAttributes.USERNAME)
    if username is None:
        raise credentials_exception
    
    expires: datetime | None = payload.get(TokenAttributes.EXPIRES)
    if expires is None or datetime.now(timezone.utc) > expires:
        raise token_expired_exception
    
    user_scopes = payload.get(TokenAttributes.SCOPES, None)
    if not _check_scopes(route_scopes.scopes, user_scopes):
        raise perm_level_exception

    return username