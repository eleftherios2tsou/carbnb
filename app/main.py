from fastapi import FastAPI

app = FastAPI(title="CarBnB Backend")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
