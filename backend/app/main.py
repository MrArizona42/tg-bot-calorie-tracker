from fastapi import FastAPI
from api.routes.start import router as start_router
from api.routes.users import router as user_router

app = FastAPI()

app.include_router(start_router)
app.include_router(user_router)
