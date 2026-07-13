from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.repository import list_draw_numbers
from app.engine.statistics import calculate_average_sum, calculate_frequency, classify_numbers
from app.scoring.score import calculate_score, rank_games

router = APIRouter(prefix="/score", tags=["score"])


class RankRequest(BaseModel):
    games: list[list[int]]


def _validate_games(games: list[list[int]]):
    for game in games:
        if len(game) != 15 or len(set(game)) != 15 or any(n < 1 or n > 25 for n in game):
            raise HTTPException(400, f"jogo inválido: {game} (precisa de 15 números distintos entre 1 e 25)")


def _context(db: Session) -> dict:
    draws = list_draw_numbers(db, limit=50)
    if not draws:
        raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")
    frequency = calculate_frequency(draws)
    return {
        "classification": classify_numbers(frequency),
        "average_sum": calculate_average_sum(draws),
        "previous_draw": draws[-1],
    }


@router.post("/rank")
def rank(payload: RankRequest, db: Session = Depends(get_db)):
    _validate_games(payload.games)
    ctx = _context(db)
    return rank_games(
        payload.games,
        classification=ctx["classification"],
        average_sum=ctx["average_sum"],
        previous_draw=ctx["previous_draw"],
    )
