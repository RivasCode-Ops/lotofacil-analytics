from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.data.repository import check_saved_games, update_database

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
def sync(db: Session = Depends(get_db), x_cron_secret: str | None = Header(default=None)):
    """Roda a atualização de concursos + conferência dos jogos salvos numa
    chamada só. Pensado pra ser disparado por um agendador externo (cron)."""
    if settings.cron_secret and x_cron_secret != settings.cron_secret:
        raise HTTPException(401, "não autorizado")

    draws_result = update_database(db, last_n=50)
    check_result = check_saved_games(db)
    return {"draws_update": draws_result, "saved_games_check": check_result}
