from fastapi import APIRouter

from app.generator.combinations import generate_combination

router = APIRouter(prefix="/combinations", tags=["combinations"])


@router.get("/sample")
def sample(n: int = 5):
    return {"combinations": [generate_combination() for _ in range(n)]}
