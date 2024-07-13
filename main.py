from fastapi import FastAPI
from app.users.Router import router as users_router
# import SubRouter

app = FastAPI()

# /

# /users/
app.include_router(users_router)