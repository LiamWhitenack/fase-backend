import pytest
import os
from httpx import AsyncClient
from fastapi import FastAPI

app = FastAPI(
    root_path=os.getenv(key=""),  # type: ignore
)


@pytest.mark.anyio
async def test_hello_world() -> None:
    client = AsyncClient(app=app, base_url="http://localhost")
    response = await client.get("/")

    assert response.status_code == 200
