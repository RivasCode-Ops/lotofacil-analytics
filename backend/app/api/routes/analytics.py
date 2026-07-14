from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.analytics.calibration import analyze_correlations, backtest_scoring, suggest_weights
from app.analytics.performance import evaluate_performance
from app.core.config import settings
from app.core.database import get_db
from app.data.models import ScoreWeights
from app.data.repository import get_draw_by_contest, get_last_draw, save_score_weights

router = APIRouter(prefix="/analytics", tags=["analytics"])


class EvaluateRequest(BaseModel):
    games: list[list[int]]
    contest: int | None = None


@router.post("/evaluate")
def evaluate(payload: EvaluateRequest, db: Session = Depends(get_db)):
    if payload.contest is not None:
        draw = get_draw_by_contest(db, payload.contest)
        if not draw:
            raise HTTPException(404, f"concurso {payload.contest} não encontrado no banco")
    else:
        draw = get_last_draw(db)
        if not draw:
            raise HTTPException(400, "sem concursos no banco — rode POST /api/draws/update primeiro")

    draw_numbers = [int(n) for n in draw.numbers.split(",")]
    resultado = evaluate_performance(payload.games, draw_numbers)
    resultado["concurso"] = draw.contest
    return resultado


@router.post("/calibrate")
def calibrate(
    games_per_draw: int = 200,
    db: Session = Depends(get_db),
    x_cron_secret: str | None = Header(default=None),
):
    """Backtest estatístico: gera jogos aleatórios contra cada concurso
    histórico e testa se algum critério do score correlaciona de verdade com
    acertos. Só ajusta os pesos se achar correlação estatisticamente
    significativa — o esperado é não achar (loteria é sorteio independente)."""
    if settings.cron_secret and x_cron_secret != settings.cron_secret:
        raise HTTPException(401, "não autorizado")

    data_points = backtest_scoring(db, games_per_draw=games_per_draw)
    if not data_points:
        raise HTTPException(400, "poucos concursos no banco pra calibrar — rode POST /api/draws/update primeiro")

    analysis = analyze_correlations(data_points)
    weights = suggest_weights(analysis["correlacoes"])
    save_score_weights(db, weights, sample_size=analysis["amostra"], conclusion=analysis["conclusao"])

    return {**analysis, "pesos_aplicados": weights}


@router.get("/weights")
def weights(db: Session = Depends(get_db)):
    row = db.get(ScoreWeights, 1)
    if not row:
        return {
            "pesos": {"paridade": 1.0, "faixa": 1.0, "frequencia": 1.0, "soma": 1.0, "repeticao": 1.0},
            "updated_at": None,
            "sample_size": 0,
            "conclusion": "nunca calibrado — usando pesos padrão (todos 1.0)",
        }
    return {
        "pesos": {
            "paridade": row.paridade,
            "faixa": row.faixa,
            "frequencia": row.frequencia,
            "soma": row.soma,
            "repeticao": row.repeticao,
        },
        "updated_at": row.updated_at,
        "sample_size": row.sample_size,
        "conclusion": row.conclusion,
    }
