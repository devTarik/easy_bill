from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.receipt.views
import src.user.views
from src.config import settings
from src.db import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await dispose_engine()


app = FastAPI(lifespan=lifespan, openapi_url=settings.openapi_url)


app.include_router(src.user.views.router, prefix="/user", tags=["User"])
app.include_router(src.receipt.views.router, prefix="/receipt", tags=["Receipt"])


@app.get("/ping")
def ping():
    return {"msg": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=8081, host="127.0.0.1", reload=True)
