from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="CarBnB Backend")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.app_env}
