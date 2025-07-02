from fastapi import FastAPI

from app.routes import router as addresses_router


app = FastAPI(
    root_path="/api/v1"
)

app.include_router(addresses_router)
