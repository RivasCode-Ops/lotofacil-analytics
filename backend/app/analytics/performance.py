PRIZE_TIERS = (11, 12, 13, 14, 15)


def calculate_hits(game: list[int], draw: list[int]) -> int:
    """Quantidade de números do `game` que aparecem no `draw` real."""
    return len(set(game) & set(draw))


def evaluate_performance(games: list[list[int]], draw: list[int]) -> dict:
    """Compara um lote de jogos com o resultado real de um concurso e mede
    desempenho: acertos por jogo, distribuição, faixas premiadas (11 a 15
    acertos), média, melhor e pior jogo."""
    acertos_por_jogo = [{"game": game, "acertos": calculate_hits(game, draw)} for game in games]
    acertos = [item["acertos"] for item in acertos_por_jogo]

    distribuicao: dict[int, int] = {}
    for a in acertos:
        distribuicao[a] = distribuicao.get(a, 0) + 1

    premiados = {faixa: distribuicao.get(faixa, 0) for faixa in PRIZE_TIERS}

    return {
        "total_jogos": len(games),
        "acertos_por_jogo": acertos_por_jogo,
        "distribuicao_acertos": dict(sorted(distribuicao.items())),
        "premiados": premiados,
        "media_acertos": sum(acertos) / len(acertos) if acertos else 0.0,
        "melhor_jogo": max(acertos_por_jogo, key=lambda h: h["acertos"]) if acertos_por_jogo else None,
        "pior_jogo": min(acertos_por_jogo, key=lambda h: h["acertos"]) if acertos_por_jogo else None,
    }
