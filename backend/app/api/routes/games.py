from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.repository import get_score_weights, list_draw_numbers
from app.engine.statistics import (
    calculate_average_sum,
    calculate_frequency,
    calculate_gaps,
    classify_by_gap,
    classify_numbers,
)
from app.generator.games import generate_games

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/generate")
def generate(n: int = 5, db: Session = Depends(get_db)):
    if n < 1 or n > 50:
        raise HTTPException(400, "n deve estar entre 1 e 50")

    draws = list_draw_numbers(db, limit=50)
    if not draws:
        raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")

    frequency = calculate_frequency(draws)
    jogos = generate_games(
        n,
        classification=classify_numbers(frequency),
        average_sum=calculate_average_sum(draws),
        previous_draw=draws[-1],
        gap_classification=classify_by_gap(calculate_gaps(draws)),
        weights=get_score_weights(db),
    )
    return jogos
