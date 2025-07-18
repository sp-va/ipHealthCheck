from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as addresses_router


app = FastAPI(
    root_path="/api/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(addresses_router)