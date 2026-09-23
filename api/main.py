from fastapi import FastAPI

from api.routers.bookings import router as bookings_router
from api.routers.rooms import router as rooms_router
from api.routers.availability import router as availability_router
from api.routers.auth import router as auth_router

app = FastAPI(
    title="BoardBot API",
    description="AI-powered workspace booking and scheduling API",
    version="1.0.0",
)


print("REGISTERING ROOMS ROUTER")
app.include_router(rooms_router)

print("REGISTERING BOOKINGS ROUTER")
app.include_router(bookings_router)

print("REGISTERING AVAILABILITY ROUTER")
app.include_router(availability_router)

print("REGISTERING AUTH ROUTER")
app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "boardbot-api",
    }