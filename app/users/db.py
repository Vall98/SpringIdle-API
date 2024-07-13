from db import BaseTable
from pydantic import BaseModel

USERS_TABLE_NAME = 'users'

class UserTable(BaseTable):
    def __init__(self):
        BaseTable.__init__(self, USERS_TABLE_NAME)
    
    def get_schema():
        key_schema = [
            {"AttributeName": "username", "KeyType": "S"},  # Partition key
        ]
        attr_def = [
            {"AttributeName": "username", "AttributeType": "S"},
            {"AttributeName": "password", "AttributeType": "S"},
        ]
        return key_schema, attr_def

    def add_user(self, username, hashed):
        if self.get_user(username) is not None:
            return None
        user = self.add_entry({"username": username, "password": hashed}, username)
        if user:
            return User(**user)
        return None
    
    def get_user(self, username, query=None, include_pwd=False):
        if not query:
            user = self.get_entry({"username": username}, username)
        else:
            user = self.get_query(query, username)
        if user:
            user['password'] = None if not include_pwd else bytes(user['password'])
            return User(**user)
        return None
    
    def get_users(self):
        pass

    def update_user(self, username):
        return self.update_entry("", "", "", username) #TBD

user_table = UserTable()

class User(BaseModel):
    username : str
    password : bytes | None