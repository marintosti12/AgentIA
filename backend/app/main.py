from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.services import lichess_service, stockfish_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    stockfish_service.init_engine()
    yield
    stockfish_service.shutdown_engine()
    await lichess_service.close_client()


app = FastAPI(
    title="Agent IA Echecs - FFE",
    description="Agent IA pour l'apprentissage des ouvertures aux echecs",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")
