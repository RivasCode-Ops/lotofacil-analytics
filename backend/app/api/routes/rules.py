from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.repository import list_draw_numbers
from app.engine.rules import validate_combination
from app.engine.statistics import calculate_average_sum, calculate_frequency, classify_numbers

router = APIRouter(prefix="/rules", tags=["rules"])


class ValidateRequest(BaseModel):
    numbers: list[int]


@router.post("/validate")
def validate(payload: ValidateRequest, db: Session = Depends(get_db)):
    if len(payload.numbers) != 15 or len(set(payload.numbers)) != 15:
        raise HTTPException(400, "informe exatamente 15 números distintos")
    if any(n < 1 or n > 25 for n in payload.numbers):
        raise HTTPException(400, "números devem estar entre 1 e 25")

    draws = list_draw_numbers(db, limit=50)
    if not draws:
        raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")

    frequency = calculate_frequency(draws)
    classification = classify_numbers(frequency)
    average_sum = calculate_average_sum(draws)
    previous_draw = draws[-1]

    return validate_combination(
        payload.numbers,
        classification=classification,
        previous_draw=previous_draw,
        average_sum=average_sum,
    )
