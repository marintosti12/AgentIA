import sys
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.services import lichess_service, milvus_service, mongodb_service, stockfish_service, youtube_service


def _init_with_timeout(name, func, timeout=30):
    result = {"ok": False, "error": None}

    def run():
        try:
            func()
            result["ok"] = True
        except Exception as e:
            result["error"] = e

    t = threading.Thread(target=run)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        print(f"[STARTUP] {name} TIMEOUT after {timeout}s - skipping", flush=True)
    elif result["ok"]:
        print(f"[STARTUP] {name} OK", flush=True)
    else:
        print(f"[STARTUP] {name} FAILED: {result['error']}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Initializing services...", flush=True)

    _init_with_timeout("Stockfish", stockfish_service.init_engine, timeout=10)
    _init_with_timeout("YouTube", youtube_service.init_youtube, timeout=5)
    _init_with_timeout("MongoDB", mongodb_service.init_mongodb, timeout=10)

    # Milvus en arriere-plan pour ne pas bloquer le demarrage
    def _bg_milvus():
        import time
        for attempt in range(5):
            try:
                milvus_service.init_milvus()
                print(f"[STARTUP] Milvus OK (attempt {attempt + 1})", flush=True)
                return
            except Exception as e:
                print(f"[STARTUP] Milvus attempt {attempt + 1} failed: {e}", flush=True)
                time.sleep(10)
        print("[STARTUP] Milvus FAILED after 5 attempts", flush=True)

    threading.Thread(target=_bg_milvus, daemon=True).start()

    print("[STARTUP] Done - server ready (Milvus loading in background)", flush=True)
    sys.stdout.flush()
    yield

    stockfish_service.shutdown_engine()
    await lichess_service.close_client()
    milvus_service.close_milvus()
    await mongodb_service.close_mongodb()


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
