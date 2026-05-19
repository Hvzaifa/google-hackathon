from fastapi import FastAPI

from routes.orchestration_routes import router as orchestration_router
from routes.feedback_routes import router as feedback_router
from routes.booking_routes import router as booking_router

app = FastAPI(title="ServisAI Agent Backend")


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(orchestration_router)
app.include_router(feedback_router)
app.include_router(booking_router)



