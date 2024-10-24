from fastapi import APIRouter

router = APIRouter()


@router.get("/ex1")
async def example1(data: str):

    return {"router": "example-1", "data": data}
