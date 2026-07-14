from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.performance import calculate_hits
from app.data.client import DataSourceError, fetch_results
from app.data.models import Draw, SavedGame


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


def save_games(db: Session, games: list[dict], target_contest: int) -> list[SavedGame]:
    """Anota jogos ('jogo do dia') pra conferir depois contra `target_contest`."""
    now = datetime.now(timezone.utc).isoformat()
    saved = []
    for g in games:
        numbers_str = ",".join(str(n) for n in sorted(g["numbers"]))
        entry = SavedGame(
            numbers=numbers_str,
            score=g.get("score", 0.0),
            target_contest=target_contest,
            created_at=now,
            checked=False,
            hits=None,
        )
        db.add(entry)
        saved.append(entry)
    db.commit()
    for entry in saved:
        db.refresh(entry)
    return saved


def list_saved_games(db: Session, only_unchecked: bool = False) -> list[SavedGame]:
    stmt = select(SavedGame).order_by(SavedGame.id.desc())
    if only_unchecked:
        stmt = stmt.where(SavedGame.checked.is_(False))
    return list(db.scalars(stmt))


def check_saved_games(db: Session) -> dict:
    """Confere os jogos anotados ainda não conferidos contra o resultado real
    do concurso alvo (se já tiver saído e estiver no banco)."""
    pending = list(db.scalars(select(SavedGame).where(SavedGame.checked.is_(False))))
    checked_now = 0
    for game in pending:
        draw = get_draw_by_contest(db, game.target_contest)
        if not draw:
            continue
        draw_numbers = [int(n) for n in draw.numbers.split(",")]
        game_numbers = [int(n) for n in game.numbers.split(",")]
        game.hits = calculate_hits(game_numbers, draw_numbers)
        game.checked = True
        checked_now += 1
    db.commit()
    return {"checked_now": checked_now, "still_pending": len(pending) - checked_now}
