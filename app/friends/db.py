from pydantic import BaseModel
from db import BaseTable

FRIENDS_TABLE_NAME = 'friends'

class FriendsTable(BaseTable):
    def __init__(self):
        BaseTable.__init__(self, FRIENDS_TABLE_NAME, "username")

    def add_friend(self, username: str, friend: str):
        query = { "username": username }
        update_expr = "ADD friends :friend"
        expr_attr_values = { ":friend": [friend] },
        friends = self.update_item(query, update_expr, expr_attr_values, username)
        if friends:
            return Friends(username=username, friends=set(**friends))
        return None # unreachable, if the update fails an error is raised
    
    def remove_friend(self, username: str, friend: str):
        query = { "username": username }
        update_expr = "DELETE friends :friend"
        expr_attr_values = { ":friend": [friend] },
        friends = self.update_item(query, update_expr, expr_attr_values, username)
        if friends:
            return Friends(username=username, friends=set(**friends))
        return None

    def get_user_friends(self, username: str, query=None):
        if not query:
            friends = self.get_item({"username": username}, username)
        else:
            friends = self.query(query, username)
        if friends:
            return Friends(username=username, friends=set(**friends))
        return None

friends_table = FriendsTable()

class Friends(BaseModel):
    username : str
    friends : set