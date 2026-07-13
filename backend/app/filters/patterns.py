ROWS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25)]  # linhas do volante (grade 5x5)


def has_sequence(combination: list[int], min_length: int = 4) -> bool:
    """True se existir uma sequência de `min_length` ou mais números consecutivos."""
    ordered = sorted(combination)
    run = 1
    for prev, curr in zip(ordered, ordered[1:]):
        run = run + 1 if curr == prev + 1 else 1
        if run >= min_length:
            return True
    return False


def is_balanced_distribution(combination: list[int], max_per_row: int = 4, max_per_col: int = 4) -> bool:
    """False se alguma linha ou coluna do volante (grade 5x5: 1-5, 6-10, ...,
    21-25 em linhas; colunas verticais de 5 em 5) concentrar números demais."""
    combo_set = set(combination)

    for low, high in ROWS:
        if sum(1 for n in combo_set if low <= n <= high) > max_per_row:
            return False

    for col in range(5):
        column_numbers = {col + 1 + 5 * row for row in range(5)}
        if len(combo_set & column_numbers) > max_per_col:
            return False

    return True


def is_valid_pattern(combination: list[int]) -> bool:
    """Filtro eliminatório combinado: sem sequência longa e com distribuição
    equilibrada no volante."""
    return not has_sequence(combination) and is_balanced_distribution(combination)
