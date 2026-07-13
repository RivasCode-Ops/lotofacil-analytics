from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analytics.performance import evaluate_performance
from app.core.database import get_db
from app.data.repository import get_draw_by_contest, get_last_draw

router = APIRouter(prefix="/analytics", tags=["analytics"])


class EvaluateRequest(BaseModel):
    games: list[list[int]]
    contest: int | None = None


@router.post("/evaluate")
def evaluate(payload: EvaluateRequest, db: Session = Depends(get_db)):
    if payload.contest is not None:
        draw = get_draw_by_contest(db, payload.contest)
        if not draw:
            raise HTTPException(404, f"concurso {payload.contest} não encontrado no banco")
    else:
        draw = get_last_draw(db)
        if not draw:
            raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")

    draw_numbers = [int(n) for n in draw.numbers.split(",")]
    resultado = evaluate_performance(payload.games, draw_numbers)
    resultado["concurso"] = draw.contest
    return resultado
