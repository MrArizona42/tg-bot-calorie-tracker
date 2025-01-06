from fastapi import FastAPI
from api.routes.start import router as start_router

app = FastAPI()

app.include_router(start_router)

# Connect to database when app starts
# @app.on_event("startup")
# async def startup():
#     await database.connect()

# Disconnect from database when app stops
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

