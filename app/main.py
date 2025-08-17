from fastapi import FastAPI
from app.config import settings
from app.routers import debug, auth, me

app = FastAPI(title="CarBnB Backend")
app.include_router(debug.router)
app.include_router(auth.router)
app.include_router(me.router)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.app_env}

