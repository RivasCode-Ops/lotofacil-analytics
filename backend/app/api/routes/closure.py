from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.closure.wheel import generate_closure

router = APIRouter(prefix="/closure", tags=["closure"])


class ClosureRequest(BaseModel):
    numbers: list[int]


@router.post("/generate")
def generate(payload: ClosureRequest):
    try:
        jogos = generate_closure(payload.numbers)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    return {"base_size": len(set(payload.numbers)), "total_jogos": len(jogos), "jogos": jogos}
