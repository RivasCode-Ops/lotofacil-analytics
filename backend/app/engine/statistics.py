PRIMES_1_25 = {2, 3, 5, 7, 11, 13, 17, 19, 23}


def calculate_frequency(draws: list[list[int]]) -> dict[int, int]:
    frequency = {n: 0 for n in range(1, 26)}
    for draw in draws:
        for number in draw:
            frequency[number] += 1
    return frequency


def classify_numbers(frequency: dict[int, int]) -> dict[str, list[int]]:
    """Divide os 25 números em tercis de frequência: quentes, médios, frios."""
    ranked = sorted(frequency.items(), key=lambda kv: kv[1], reverse=True)
    third = len(ranked) // 3
    hot = sorted(n for n, _ in ranked[:third])
    cold = sorted(n for n, _ in ranked[-third:])
    medium = sorted(n for n, _ in ranked[third: len(ranked) - third])
    return {"quentes": hot, "medios": medium, "frios": cold}


def calculate_average_sum(draws: list[list[int]]) -> float:
    if not draws:
        return 0.0
    return sum(sum(draw) for draw in draws) / len(draws)


def calculate_parity(draws: list[list[int]]) -> dict:
    if not draws:
        return {"pares_media": 0.0, "impares_media": 0.0, "distribuicao_pares": {}}
    pares_por_concurso = [sum(1 for n in draw if n % 2 == 0) for draw in draws]
    distribuicao: dict[int, int] = {}
    for p in pares_por_concurso:
        distribuicao[p] = distribuicao.get(p, 0) + 1
    media_pares = sum(pares_por_concurso) / len(draws)
    return {
        "pares_media": media_pares,
        "impares_media": 15 - media_pares,
        "distribuicao_pares": dict(sorted(distribuicao.items())),
    }


def calculate_primes(draws: list[list[int]]) -> dict:
    if not draws:
        return {"primos_media": 0.0, "distribuicao_primos": {}}
    primos_por_concurso = [sum(1 for n in draw if n in PRIMES_1_25) for draw in draws]
    distribuicao: dict[int, int] = {}
    for p in primos_por_concurso:
        distribuicao[p] = distribuicao.get(p, 0) + 1
    return {
        "primos_media": sum(primos_por_concurso) / len(draws),
        "distribuicao_primos": dict(sorted(distribuicao.items())),
    }


def calculate_repetition(draws: list[list[int]]) -> dict:
    """Números repetidos de um concurso para o seguinte. `draws` deve estar em
    ordem cronológica (mais antigo primeiro)."""
    if len(draws) < 2:
        return {"repeticao_media": 0.0, "repeticoes": []}
    repeticoes = [len(set(anterior) & set(atual)) for anterior, atual in zip(draws, draws[1:])]
    return {
        "repeticao_media": sum(repeticoes) / len(repeticoes),
        "repeticoes": repeticoes,
    }


def get_statistics_summary(draws: list[list[int]]) -> dict:
    """`draws` em ordem cronológica (mais antigo primeiro). Saída estruturada
    pronta para consumo pelo resto do sistema (regras, score, API)."""
    frequency = calculate_frequency(draws)
    return {
        "total_concursos_analisados": len(draws),
        "frequencia": frequency,
        "classificacao": classify_numbers(frequency),
        "soma_media": calculate_average_sum(draws),
        "paridade": calculate_parity(draws),
        "primos": calculate_primes(draws),
        "repeticao": calculate_repetition(draws),
    }
