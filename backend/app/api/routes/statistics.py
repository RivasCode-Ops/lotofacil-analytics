from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.repository import list_draw_numbers
from app.engine.statistics import get_statistics_summary

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("")
def statistics(limit: int = 50, db: Session = Depends(get_db)):
    draws = list_draw_numbers(db, limit=limit)
    return get_statistics_summary(draws)
