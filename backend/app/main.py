from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def start():
    return "Hi there! It's your FastAPI app responding!"

# Connect to database when app starts
# @app.on_event("startup")
# async def startup():
#     await database.connect()

# Disconnect from database when app stops
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

