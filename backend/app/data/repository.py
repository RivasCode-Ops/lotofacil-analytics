from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.client import DataSourceError, fetch_results
from app.data.models import Draw


def update_database(db: Session, last_n: int = 50) -> dict:
    try:
        results = fetch_results(last_n=last_n)
    except DataSourceError as exc:
        return {"inserted": 0, "updated": 0, "error": str(exc)}

    inserted = 0
    updated = 0
    for r in results:
        numbers_str = ",".join(str(n) for n in r["numbers"])
        existing = db.scalar(select(Draw).where(Draw.contest == r["contest"]))
        if existing:
            changed = existing.numbers != numbers_str
            if r["draw_date"] and existing.draw_date != r["draw_date"]:
                existing.draw_date = r["draw_date"]
                changed = True
            existing.numbers = numbers_str
            if changed:
                updated += 1
        else:
            db.add(Draw(contest=r["contest"], draw_date=r["draw_date"] or "", numbers=numbers_str))
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated, "total_fetched": len(results)}


def get_last_draw(db: Session) -> Draw | None:
    return db.scalar(select(Draw).order_by(Draw.contest.desc()).limit(1))


def get_draw_by_contest(db: Session, contest: int) -> Draw | None:
    return db.scalar(select(Draw).where(Draw.contest == contest))


def list_draws(db: Session, limit: int = 50) -> list[Draw]:
    return list(db.scalars(select(Draw).order_by(Draw.contest.desc()).limit(limit)))


def list_draw_numbers(db: Session, limit: int = 50) -> list[list[int]]:
    """Últimos `limit` concursos, em ordem cronológica (mais antigo primeiro)."""
    draws = list(db.scalars(select(Draw).order_by(Draw.contest.desc()).limit(limit)))
    draws.reverse()
    return [[int(n) for n in d.numbers.split(",")] for d in draws]
