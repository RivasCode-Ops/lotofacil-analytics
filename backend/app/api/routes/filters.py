from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.filters.patterns import has_sequence, is_balanced_distribution, is_valid_pattern

router = APIRouter(prefix="/filters", tags=["filters"])


class ValidateRequest(BaseModel):
    numbers: list[int]


@router.post("/validate")
def validate(payload: ValidateRequest):
    if len(payload.numbers) != 15 or len(set(payload.numbers)) != 15:
        raise HTTPException(400, "informe exatamente 15 números distintos")
    if any(n < 1 or n > 25 for n in payload.numbers):
        raise HTTPException(400, "números devem estar entre 1 e 25")

    return {
        "tem_sequencia": has_sequence(payload.numbers),
        "distribuicao_equilibrada": is_balanced_distribution(payload.numbers),
        "valido": is_valid_pattern(payload.numbers),
    }
