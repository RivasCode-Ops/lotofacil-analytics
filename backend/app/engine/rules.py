from app.engine.statistics import PRIMES_1_25

RANGE_BOUNDS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25)]


def validate_ranges(combination: list[int], min_per_range: int = 1) -> bool:
    """Cada faixa de 5 dezenas (1-5, 6-10, 11-15, 16-20, 21-25) deve ter pelo
    menos `min_per_range` números — evita concentração numa única faixa."""
    for low, high in RANGE_BOUNDS:
        if sum(1 for n in combination if low <= n <= high) < min_per_range:
            return False
    return True


def validate_parity(combination: list[int], allowed: tuple[int, ...] = (7, 8)) -> bool:
    pares = sum(1 for n in combination if n % 2 == 0)
    return pares in allowed


def validate_primes(combination: list[int], min_primes: int = 4, max_primes: int = 6) -> bool:
    primos = sum(1 for n in combination if n in PRIMES_1_25)
    return min_primes <= primos <= max_primes


def validate_frequency(
    combination: list[int],
    classification: dict[str, list[int]],
    min_quentes: int = 1,
    min_frios: int = 1,
) -> bool:
    """Exige presença mínima de números quentes e frios (evita apostar só nos médios)."""
    quentes = set(classification.get("quentes", []))
    frios = set(classification.get("frios", []))
    combo_set = set(combination)
    return len(combo_set & quentes) >= min_quentes and len(combo_set & frios) >= min_frios


def validate_repetition(
    combination: list[int],
    previous_draw: list[int],
    min_rep: int = 8,
    max_rep: int = 10,
) -> bool:
    repeticao = len(set(combination) & set(previous_draw))
    return min_rep <= repeticao <= max_rep


def validate_sum(combination: list[int], average_sum: float, tolerance: float = 0.10) -> bool:
    total = sum(combination)
    low = average_sum * (1 - tolerance)
    high = average_sum * (1 + tolerance)
    return low <= total <= high


def validate_combination(
    combination: list[int],
    *,
    classification: dict[str, list[int]],
    previous_draw: list[int],
    average_sum: float,
) -> dict:
    """Roda todas as regras e retorna o detalhamento + veredito final."""
    resultados = {
        "faixas": validate_ranges(combination),
        "paridade": validate_parity(combination),
        "primos": validate_primes(combination),
        "frequencia": validate_frequency(combination, classification),
        "repeticao": validate_repetition(combination, previous_draw),
        "soma": validate_sum(combination, average_sum),
    }
    resultados["valido"] = all(resultados.values())
    return resultados
