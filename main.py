from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth,
    cars,
    customers,
    offer,
    sale,
    payment,
    test_drive,
    user,
    inventory,
    dashboard,
    carMedia,
    Contact,
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://dealership-frontend-ip.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from services.limiter import limiter  # Import the limiter instance

# Attach middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# Custom error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429, content={"detail": "Too many requests, slow down!"}
    )


app.include_router(auth.router)
app.include_router(cars.publicRouter)
app.include_router(cars.router)
app.include_router(customers.router)
app.include_router(offer.router)
app.include_router(sale.router)
app.include_router(payment.router)
app.include_router(test_drive.router)
app.include_router(user.router)
app.include_router(inventory.router)
app.include_router(dashboard.router)
app.include_router(carMedia.media_router)
app.include_router(offer.publicRouter)
app.include_router(Contact.router)