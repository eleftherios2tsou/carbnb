from fastapi import FastAPI
from app.config import settings
from app.routers import debug, auth, me
from app.profiles import routers as profiles_router
from app.cars import routers as cars_router
from app.photos import routers as s3_router
from app.availability import router as availability_router 
from app.search import router as search_router

app = FastAPI(title="CarBnB Backend")
app.include_router(debug.router)
app.include_router(auth.router)
app.include_router(me.router)
app.include_router(profiles_router.router)
app.include_router(cars_router.router)
app.include_router(s3_router.router)
app.include_router(availability_router.router)
app.include_router(search_router.router)
@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.app_env}

