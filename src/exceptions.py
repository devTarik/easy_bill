import asyncpg
from fastapi import Request
from fastapi.responses import JSONResponse

from app import app


@app.exception_handler(asyncpg.exceptions.UniqueViolationError)
async def unique_violation_exception_handler(request: Request, exc: asyncpg.exceptions.UniqueViolationError):
    return JSONResponse(status_code=400, content={"detail": "Username already registered"})
