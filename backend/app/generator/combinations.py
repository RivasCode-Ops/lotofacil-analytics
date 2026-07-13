import itertools
import random
from typing import Callable, Iterator

NUMBERS = list(range(1, 26))
GAME_SIZE = 15

Predicate = Callable[[list[int]], bool]


def generate_combination(size: int = GAME_SIZE) -> list[int]:
    """Gera uma combinação aleatória de `size` números entre 1 e 25."""
    return sorted(random.sample(NUMBERS, size))


def stream_combinations(size: int = GAME_SIZE, shuffle: bool = False) -> Iterator[list[int]]:
    """Gera combinações sob demanda. Usa itertools.combinations, que produz cada
    item on-the-fly — nunca materializa o espaço completo (C(25,15) ≈ 3.27 milhões)
    em memória. `shuffle=True` embaralha em blocos, sem carregar tudo de uma vez."""
    combos = itertools.combinations(NUMBERS, size)

    if not shuffle:
        for combo in combos:
            yield list(combo)
        return

    block_size = 5000
    buffer: list[list[int]] = []
    for combo in combos:
        buffer.append(list(combo))
        if len(buffer) >= block_size:
            random.shuffle(buffer)
            yield from buffer
            buffer = []
    if buffer:
        random.shuffle(buffer)
        yield from buffer


def filter_combination(combination: list[int], predicates: list[Predicate]) -> bool:
    """Aplica os predicados em ordem e para no primeiro que falhar (short-circuit)."""
    return all(predicate(combination) for predicate in predicates)


def filter_stream(
    combinations: Iterator[list[int]],
    predicates: list[Predicate],
    limit: int | None = None,
) -> Iterator[list[int]]:
    """Filtragem progressiva: consome o stream de combinações e produz só as
    válidas, sem nunca materializar o conjunto inteiro. Para assim que atinge
    `limit` (se informado), evitando percorrer o resto do espaço de busca."""
    count = 0
    for combo in combinations:
        if filter_combination(combo, predicates):
            yield combo
            count += 1
            if limit is not None and count >= limit:
                return
