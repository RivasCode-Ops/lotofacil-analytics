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


def calculate_new_vs_repeat(draws: list[list[int]]) -> dict:
    """Distribuição de quantos números se repetem vs. são novos de um
    concurso para o seguinte (novos = 15 - repetidos)."""
    if len(draws) < 2:
        return {"distribuicao_repetidos": {}, "distribuicao_novos": {}}
    dist_rep: dict[int, int] = {}
    dist_novos: dict[int, int] = {}
    for anterior, atual in zip(draws, draws[1:]):
        rep = len(set(anterior) & set(atual))
        novos = 15 - rep
        dist_rep[rep] = dist_rep.get(rep, 0) + 1
        dist_novos[novos] = dist_novos.get(novos, 0) + 1
    return {
        "distribuicao_repetidos": dict(sorted(dist_rep.items())),
        "distribuicao_novos": dict(sorted(dist_novos.items())),
    }


def calculate_gaps(draws: list[list[int]]) -> dict[int, int]:
    """Atraso de cada número: quantos concursos se passaram desde a última
    vez que saiu (0 = saiu no concurso mais recente). `draws` em ordem
    cronológica (mais antigo primeiro)."""
    gaps = {}
    for n in range(1, 26):
        gap = len(draws)  # nunca saiu na amostra
        for i in range(len(draws) - 1, -1, -1):
            if n in draws[i]:
                gap = len(draws) - 1 - i
                break
        gaps[n] = gap
    return gaps


def classify_by_gap(gaps: dict[int, int]) -> dict[str, list[int]]:
    """Divide os 25 números em tercis por atraso: atrasados (maior gap),
    médios, recentes (saíram há pouco)."""
    ranked = sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)
    third = len(ranked) // 3
    atrasados = sorted(n for n, _ in ranked[:third])
    recentes = sorted(n for n, _ in ranked[-third:])
    medios = sorted(n for n, _ in ranked[third: len(ranked) - third])
    return {"atrasados": atrasados, "medios": medios, "recentes": recentes}


def calculate_gap_distribution(draws: list[list[int]]) -> dict:
    """Intervalo (em concursos) entre aparições consecutivas de cada número,
    agregado numa distribuição — gap=1 significa que saiu em concursos
    seguidos, gap=2 significa que 'pulou' um concurso (intercalado), etc.
    Compara com a distribuição teórica esperada num sorteio aleatório puro
    (geométrica, p=15/25=0.6): se os dados reais baterem com a teórica —
    e devem bater — não há padrão de intercalação real explorável."""
    observado: dict[int, int] = {}
    for n in range(1, 26):
        aparicoes = [i for i, draw in enumerate(draws) if n in draw]
        for a, b in zip(aparicoes, aparicoes[1:]):
            gap = b - a
            observado[gap] = observado.get(gap, 0) + 1

    total = sum(observado.values())
    p = 15 / 25
    max_gap = max(observado.keys(), default=1)
    teorico = {}
    for gap in range(1, max_gap + 1):
        prob = ((1 - p) ** (gap - 1)) * p
        teorico[gap] = round(prob * total, 1)

    return {
        "observado": dict(sorted(observado.items())),
        "teorico_sorteio_aleatorio": teorico,
        "total_intervalos": total,
    }


def get_statistics_summary(draws: list[list[int]]) -> dict:
    """`draws` em ordem cronológica (mais antigo primeiro). Saída estruturada
    pronta para consumo pelo resto do sistema (regras, score, API)."""
    frequency = calculate_frequency(draws)
    gaps = calculate_gaps(draws)
    return {
        "total_concursos_analisados": len(draws),
        "frequencia": frequency,
        "classificacao": classify_numbers(frequency),
        "soma_media": calculate_average_sum(draws),
        "paridade": calculate_parity(draws),
        "primos": calculate_primes(draws),
        "repeticao": calculate_repetition(draws),
        "novos_vs_repetidos": calculate_new_vs_repeat(draws),
        "atraso": gaps,
        "classificacao_atraso": classify_by_gap(gaps),
        "distribuicao_intervalos": calculate_gap_distribution(draws),
    }
