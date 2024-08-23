from app.friends import controller
from app.friends.db import Friends
from app.users.scopes import Scopes
from fastapi import APIRouter, Security
from typing import Annotated

router = APIRouter(prefix="/friends")

@router.get('/')
def get_home_page():
    return {"Hello": "World", "status": 200}

@router.get('/get')
async def get_friends(friends: Annotated[Friends, Security(controller.get_friends, scopes=[Scopes.FRIENDS_GET])]):
    return friends

@router.get('/{username}/get')
async def get_friends(username: str, friends: Annotated[Friends, Security(controller.get_user_friends, scopes=[Scopes.FRIENDS_GET_ANY_USER])]):
    return friends