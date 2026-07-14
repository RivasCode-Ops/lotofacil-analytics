from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.models import SavedGame
from app.data.repository import check_saved_games, get_last_draw, list_saved_games, save_games

router = APIRouter(prefix="/saved-games", tags=["saved-games"])


class GameEntry(BaseModel):
    game: list[int]
    total: float = 0.0


class SaveGamesRequest(BaseModel):
    games: list[GameEntry]
    target_contest: int | None = None


def _serialize(entry: SavedGame) -> dict:
    return {
        "id": entry.id,
        "numbers": [int(n) for n in entry.numbers.split(",")],
        "score": entry.score,
        "target_contest": entry.target_contest,
        "created_at": entry.created_at,
        "checked": entry.checked,
        "hits": entry.hits,
    }


@router.post("")
def create(payload: SaveGamesRequest, db: Session = Depends(get_db)):
    if not payload.games:
        raise HTTPException(400, "informe pelo menos um jogo")

    target_contest = payload.target_contest
    if target_contest is None:
        last = get_last_draw(db)
        if not last:
            raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")
        target_contest = last.contest + 1

    games = [{"numbers": g.game, "score": g.total} for g in payload.games]
    saved = save_games(db, games, target_contest)
    return [_serialize(s) for s in saved]


@router.get("")
def list_all(only_unchecked: bool = False, db: Session = Depends(get_db)):
    return [_serialize(s) for s in list_saved_games(db, only_unchecked=only_unchecked)]


@router.post("/check")
def check(db: Session = Depends(get_db)):
    return check_saved_games(db)
