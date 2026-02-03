# pull official base image
FROM python:3.13-slim-bookworm

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY pyproject.toml uv.lock /_lock/

# Synchronize dependencies.
# This layer is cached until uv.lock or pyproject.toml change.
RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen 

# after uv sync
RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync --frozen

# add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# copy project
COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
