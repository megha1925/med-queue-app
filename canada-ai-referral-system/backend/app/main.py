from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="Canada AI Referral System")
app.include_router(routes.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
