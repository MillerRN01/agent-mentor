from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Agent Mentor",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(chat_router)


@app.get("/")
async def root() -> dict:
    return {"message": "Agent Mentor backend funcionando"}
