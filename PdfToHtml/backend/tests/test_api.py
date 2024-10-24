import httpx
import pytest
import json

from app.main import app

@pytest.mark.asyncio
async def test_ex1():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/example/ex1", params={"data": "hello"})
        assert response.status_code == 200
        assert response.json() == {"router": "example-1", "data": "hello"}

@pytest.mark.asyncio
async def test_ex2():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/example/ex2", json = {"data": ["hello", "world"]})
        assert response.status_code == 200
        assert response.json() == {"router": "example-2", "data": ["hello", "world"]}