import math

from sqlalchemy.orm import Session

from app.analytics.performance import calculate_hits
from app.data.repository import list_draw_numbers
from app.engine.statistics import calculate_average_sum, calculate_frequency, classify_numbers
from app.generator.combinations import generate_combination
from app.scoring.score import calculate_score

CRITERIA = ("paridade", "faixa", "frequencia", "soma", "repeticao")

# Bonferroni aproximado para 6 testes (5 critérios + total) a ~p<0.05: 0.05/6 ≈ 0.0083 -> z ≈ 2.64
SIGNIFICANCE_Z = 2.64


def backtest_scoring(db: Session, games_per_draw: int = 200) -> list[dict]:
    """Para cada um dos concursos históricos, gera `games_per_draw` jogos
    aleatórios, pontua com os critérios atuais (pesos neutros) e mede quantos
    acertos teriam tido contra o resultado real daquele concurso.

    Isto NÃO é uma simulação de apostas reais (usa o histórico completo como
    contexto pra todos os concursos, não point-in-time) — é um teste
    estatístico: será que algum critério do score tem correlação real com
    acertos? Como a Lotofácil é um sorteio independente, a expectativa
    correta é que a resposta seja não."""
    draws = list_draw_numbers(db, limit=50)
    if len(draws) < 10:
        return []

    frequency = calculate_frequency(draws)
    classification = classify_numbers(frequency)
    average_sum = calculate_average_sum(draws)

    data_points = []
    for i, target_draw in enumerate(draws):
        previous_draw = draws[i - 1] if i > 0 else draws[-1]
        for _ in range(games_per_draw):
            game = generate_combination()
            score = calculate_score(
                game,
                classification=classification,
                average_sum=average_sum,
                previous_draw=previous_draw,
            )
            hits = calculate_hits(game, target_draw)
            data_points.append({**score["criterios"], "total": score["total"], "hits": hits})
    return data_points


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / math.sqrt(var_x * var_y)


def _is_significant(r: float, n: int) -> bool:
    """Transformação de Fisher, limiar ajustado pra múltiplas comparações."""
    if n < 4:
        return False
    if abs(r) >= 0.999999:
        return True
    z = 0.5 * math.log((1 + r) / (1 - r)) * math.sqrt(n - 3)
    return abs(z) > SIGNIFICANCE_Z


def analyze_correlations(data_points: list[dict]) -> dict:
    if not data_points:
        return {"amostra": 0, "correlacoes": {}, "conclusao": "sem dados suficientes"}

    hits = [d["hits"] for d in data_points]
    correlacoes = {}
    for criterio in (*CRITERIA, "total"):
        valores = [d[criterio] for d in data_points]
        r = _pearson(valores, hits)
        correlacoes[criterio] = {"r": round(r, 4), "significativo": _is_significant(r, len(data_points))}

    algum_significativo = any(c["significativo"] for c in correlacoes.values())
    if algum_significativo:
        conclusao = (
            "Encontrada correlação estatisticamente 'significativa' em pelo menos um critério. "
            "Cautela: com múltiplos testes, algum falso positivo é esperado por acaso mesmo sem "
            "nenhum padrão real — a Lotofácil é sorteio independente, isto não deve ser interpretado "
            "como uma forma de prever resultados."
        )
    else:
        conclusao = (
            "Nenhuma correlação significativa encontrada entre os critérios do score e os acertos "
            "reais — consistente com o esperado: a Lotofácil é um sorteio aleatório independente, "
            "sem padrão explorável nos concursos passados."
        )

    return {"amostra": len(data_points), "correlacoes": correlacoes, "conclusao": conclusao}


def suggest_weights(correlacoes: dict) -> dict:
    """Só ajusta o peso de critérios com correlação positiva E significativa.
    Para um sorteio justo, o esperado é devolver todos os pesos em 1.0."""
    weights = {}
    for criterio in CRITERIA:
        info = correlacoes.get(criterio, {})
        if info.get("significativo") and info.get("r", 0) > 0:
            weights[criterio] = round(1.0 + info["r"], 3)
        else:
            weights[criterio] = 1.0
    return weights
