from fastapi import FastAPI
from app.config import settings
from app.routers import debug

app = FastAPI(title="CarBnB Backend")
app.include_router(debug.router)

@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.app_env}
