from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.repository import get_last_draw, list_draws, update_database

router = APIRouter(prefix="/draws", tags=["draws"])


def _serialize(draw):
    return {
        "contest": draw.contest,
        "draw_date": draw.draw_date,
        "numbers": [int(n) for n in draw.numbers.split(",")],
    }


@router.post("/update")
def update_draws(last_n: int = 50, db: Session = Depends(get_db)):
    return update_database(db, last_n=last_n)


@router.get("/last")
def last_draw(db: Session = Depends(get_db)):
    draw = get_last_draw(db)
    return _serialize(draw) if draw else {"draw": None}


@router.get("")
def list_all(limit: int = 50, db: Session = Depends(get_db)):
    return [_serialize(d) for d in list_draws(db, limit=limit)]
