from app.users.scopes import Roles
from app.db import BaseTable
from pydantic import BaseModel

USERS_TABLE_NAME = 'users'

class UserTable(BaseTable):
    def __init__(self):
        BaseTable.__init__(self, USERS_TABLE_NAME, "username")

    def add_user(self, username, hashed, perm_level=Roles.USER):
        if self.get_user(username) is not None:
            return None
        user = {"username": username, "password": hashed, "perm_level": perm_level}
        self.put_item(user, username)
        user["password"] = None
        return User(**user)
    
    def get_user(self, username, query=None, include_pwd=False):
        attributes = "username,perm_level"
        if include_pwd:
            attributes += ",password"
        if not query:
            user = self.get_item({"username": username}, username, attributes=attributes)
        else:
            users = self.query(query, username)
            if users:
                user = user[0]
        if user:
            if not include_pwd:
                return User(**user)
            else:
                user['password'] = bytes(user['password'])
                return UserWithPwd(**user)
        return None
    
    def get_users(self, query=None):
        attributes = "username,perm_level"
        if query is None:
            users = self.scan("users", attributes=attributes)
        else:
            users = self.query(query, "users", attributes=attributes)
        return users

    def update_user(self, username):
        return self.update_item("", "", "", username) #TBD

user_table = UserTable()

class User(BaseModel):
    username : str
    perm_level : Roles

# We are separating the two classes to be sure to never send the password to the frontend
class UserWithPwd(User):
    password : bytes | None