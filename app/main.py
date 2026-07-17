import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.leads import router as leads_router
from app.services.embedding_service import preload

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedding model and compute catalog vectors once at startup
    # so the first real webhook call isn't the one paying for it.
    preload()
    yield


app = FastAPI(title="Signal — lead scoring API", lifespan=lifespan)
app.include_router(leads_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
