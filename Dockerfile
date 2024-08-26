FROM python:3.12.3-bullseye as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install

RUN pip install poetry

COPY pyproject.toml poetry.lock /

RUN poetry install --without dev --no-root \
    && poetry update \
    && rm -rf $POETRY_CACHE_DIR


FROM builder  as local
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH"

WORKDIR /app
