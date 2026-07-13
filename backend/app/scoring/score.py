from app.engine.rules import RANGE_BOUNDS


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _parity_score(game: list[int]) -> float:
    """100 quando pares = 7 ou 8 (centro ideal 7.5), cai com a distância."""
    pares = sum(1 for n in game if n % 2 == 0)
    distancia = abs(pares - 7.5)
    return _clip(100 * (1 - distancia / 7.5))


def _range_score(game: list[int]) -> float:
    """100 quando as 5 faixas do volante têm 3 números cada (distribuição ideal)."""
    counts = [sum(1 for n in game if low <= n <= high) for low, high in RANGE_BOUNDS]
    desvio = sum(abs(c - 3) for c in counts)
    return _clip(100 * (1 - desvio / 12))


def _frequency_score(game: list[int], classification: dict[str, list[int]]) -> float:
    """100 quando quentes/médios/frios estão representados em proporção
    equilibrada (~5 de cada, já que são 15 números de 3 grupos)."""
    grupos = ("quentes", "medios", "frios")
    game_set = set(game)
    desvio = sum(abs(len(game_set & set(classification.get(g, []))) - 5) for g in grupos)
    return _clip(100 * (1 - desvio / 10))


def _sum_score(game: list[int], average_sum: float) -> float:
    """100 quando a soma do jogo é igual à soma média histórica."""
    distancia = abs(sum(game) - average_sum)
    tolerancia = average_sum * 0.3 if average_sum else 1
    return _clip(100 * (1 - distancia / tolerancia))


def _repetition_score(game: list[int], previous_draw: list[int]) -> float:
    """100 quando a repetição com o concurso anterior é 9 (centro do ideal 8-10)."""
    overlap = len(set(game) & set(previous_draw))
    distancia = abs(overlap - 9)
    return _clip(100 * (1 - distancia / 9))


def calculate_score(
    game: list[int],
    *,
    classification: dict[str, list[int]],
    average_sum: float,
    previous_draw: list[int],
    weights: dict[str, float] | None = None,
) -> dict:
    """Pontua um jogo em cada critério (0-100) e combina num score total."""
    criterios = {
        "paridade": _parity_score(game),
        "faixa": _range_score(game),
        "frequencia": _frequency_score(game, classification),
        "soma": _sum_score(game, average_sum),
        "repeticao": _repetition_score(game, previous_draw),
    }
    pesos = weights or {k: 1 for k in criterios}
    total_peso = sum(pesos.get(k, 0) for k in criterios) or 1
    total = sum(criterios[k] * pesos.get(k, 0) for k in criterios) / total_peso
    return {"criterios": criterios, "total": round(total, 2)}


def rank_games(games: list[list[int]], **context) -> list[dict]:
    """Pontua uma lista de jogos e devolve ordenada do maior para o menor score."""
    resultados = [{"game": game, **calculate_score(game, **context)} for game in games]
    resultados.sort(key=lambda r: r["total"], reverse=True)
    return resultados
