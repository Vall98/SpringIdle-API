from app.friends.db import friends_table
from app.users.scopes import RouteScopes
from fastapi import Security
from typing import Annotated


def get_friends(username: Annotated[str, Security(RouteScopes)]):
    return friends_table.get_user_friends(username)

def get_user_friends(username: str, _: Annotated[str, Security(RouteScopes)]):
    return friends_table.get_user_friends(username)