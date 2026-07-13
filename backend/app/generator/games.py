from app.engine.rules import validate_combination
from app.filters.patterns import is_valid_pattern
from app.generator.combinations import generate_combination
from app.scoring.score import calculate_score


def generate_games(
    n: int,
    *,
    classification: dict[str, list[int]],
    average_sum: float,
    previous_draw: list[int],
    pool_multiplier: int = 5,
    max_attempts: int = 200_000,
) -> list[dict]:
    """Gera `n` jogos: amostra combinações aleatórias independentes sob demanda
    (Etapa 4), aplica filtros eliminatórios (Etapa 6) + regras (Etapa 5), pontua
    os candidatos que sobrarem (Etapa 7) e devolve os `n` melhores.

    Usa amostragem aleatória (generate_combination) em vez de varrer
    stream_combinations em ordem — varrer em ordem lexicográfica faz os
    primeiros candidatos aprovados ficarem concentrados numa vizinhança
    próxima (pouca diversidade entre os jogos gerados)."""

    def passes_rules_and_filters(combo: list[int]) -> bool:
        if not is_valid_pattern(combo):
            return False
        resultado = validate_combination(
            combo,
            classification=classification,
            previous_draw=previous_draw,
            average_sum=average_sum,
        )
        return resultado["valido"]

    pool_size = max(n * pool_multiplier, n)
    candidatos: list[list[int]] = []
    vistos: set[tuple[int, ...]] = set()
    attempts = 0
    while len(candidatos) < pool_size and attempts < max_attempts:
        attempts += 1
        combo = generate_combination()
        chave = tuple(combo)
        if chave in vistos:
            continue
        vistos.add(chave)
        if passes_rules_and_filters(combo):
            candidatos.append(combo)

    ranking = [
        {
            "game": combo,
            **calculate_score(
                combo,
                classification=classification,
                average_sum=average_sum,
                previous_draw=previous_draw,
            ),
        }
        for combo in candidatos
    ]
    ranking.sort(key=lambda r: r["total"], reverse=True)
    return ranking[:n]
