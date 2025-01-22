from fastapi import FastAPI
from api.routes.start import router as start_router
from api.routes.users import router as user_router
from api.routes.food import router as food_router
from api.routes.water import router as water_router
from api.routes.sport import router as sport_router

app = FastAPI()

app.include_router(start_router)
app.include_router(user_router)
app.include_router(food_router)
app.include_router(water_router)
app.include_router(sport_router)
