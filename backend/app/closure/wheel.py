import itertools
import math

GAME_SIZE = 15
VALID_BASE_SIZES = (18, 19, 20)


def closure_size(base_size: int) -> int:
    return math.comb(base_size, GAME_SIZE)


def generate_closure(base_numbers: list[int]) -> list[list[int]]:
    """Fechamento fechado (garantido): gera TODAS as combinações de 15 números
    a partir de uma base de 18, 19 ou 20 dezenas. Se os 15 números sorteados
    estiverem todos dentro da base, uma das combinações bate os 15 pontos.

    Tamanhos possíveis: C(18,15)=816, C(19,15)=3876, C(20,15)=15504 —
    pequenos o bastante para materializar em lista sem problema de memória
    (diferente do espaço completo de 1-25 usado na Etapa 4)."""
    base = sorted(set(base_numbers))

    if len(base) not in VALID_BASE_SIZES:
        raise ValueError(
            f"a base precisa ter 18, 19 ou 20 números distintos (recebeu {len(base)})"
        )
    if any(n < 1 or n > 25 for n in base):
        raise ValueError("números devem estar entre 1 e 25")

    return [list(combo) for combo in itertools.combinations(base, GAME_SIZE)]
