from enum import IntEnum, StrEnum

# We could define the scope description here by having a enum of tuples.
# However, this enum would not be usable with FastAPI's Security object.
class Scopes(StrEnum):

    # Users
    USER_ME = "user_me"
    USER_READ_ALL = "user_read_all"

    # Friends
    FRIENDS_ADD = "friends_add"
    FRIENDS_GET = "friends_get"
    FRIENDS_GET_ANY_USER = "friends_get_any_users"

class Roles(IntEnum):
    UNAUTHENTIFICATED = 0
    USER = 1
    PREMIUM = 2
    MODERATOR = 3
    ADMIN = 4

    ALL = ADMIN

scopes: dict[Roles, dict[Scopes, str]] = {
    Roles.UNAUTHENTIFICATED: {

    },
    Roles.USER: {
        Scopes.FRIENDS_ADD: "Add a user to the current user's friendlist.",
        Scopes.FRIENDS_GET: "Read the current user's friendlist.",
        Scopes.USER_ME: "Read information about the current user.",
    },
    Roles.PREMIUM: {

    },
    Roles.MODERATOR: {
        Scopes.FRIENDS_GET_ANY_USER: "Read any user's friendlist.",
        Scopes.USER_READ_ALL: "Read information about any user.",
    },
    Roles.ADMIN: {

    }
}
scopes[Roles.USER].update(scopes[Roles.UNAUTHENTIFICATED])
scopes[Roles.PREMIUM].update(scopes[Roles.USER])
scopes[Roles.MODERATOR].update(scopes[Roles.PREMIUM])
scopes[Roles.ADMIN].update(scopes[Roles.MODERATOR])