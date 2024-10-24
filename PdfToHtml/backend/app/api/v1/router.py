from fastapi import APIRouter

from app.api.v1.endpoints import example_get, example_post

api_router = APIRouter()
api_router.include_router(example_get.router, prefix="/example_get", tags=["example_get"])
api_router.include_router(example_post.router, prefix="/example_post", tags=["example_post"])
