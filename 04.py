import re

from typing import Tuple, TypeAlias

from lib import read_input, timer


WordSearch: TypeAlias = list[list[str]]


def parse_puzzle() -> WordSearch:
    return [list(line) for line in read_input(4)]


def find_word_in_direction(
    puzzle: WordSearch, word: str, i: int, j: int, dir: Tuple[int, int]
) -> bool:
    if word == '':
        return True

    MAX_ROW = len(puzzle) - 1
    MAX_COL = len(puzzle[0]) - 1

    if i < 0 or i > MAX_ROW or j < 0 or j > MAX_COL:
        return False

    if puzzle[i][j] != word[0]:
        return False

    return find_word_in_direction(
        puzzle, word[1:], i + dir[0], j + dir[1], dir
    )


def count_all_xmas(puzzle: WordSearch) -> int:
    count = 0
    for i, row in enumerate(puzzle):
        for j, _ in enumerate(row):
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (0, -1))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (0, +1))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (-1, -1))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (-1, 0))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (-1, +1))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (+1, -1))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (+1, 0))
            count += find_word_in_direction(puzzle, 'XMAS', i, j, (+1, +1))

    return count


def find_letter(puzzle: WordSearch, letter: str, i: int, j: int) -> bool:
    MAX_ROW = len(puzzle) - 1
    MAX_COL = len(puzzle[0]) - 1

    if i < 0 or i > MAX_ROW or j < 0 or j > MAX_COL:
        return False

    return letter == puzzle[i][j]


def find_x_mas(puzzle: WordSearch, i: int, j: int) -> bool:
    if puzzle[i][j] != 'A':
        return False

    LEGS = 'MMSS'
    for p in range(len(LEGS)):
        rotation = LEGS[p:] + LEGS[:p]
        is_x_mas = all(
            [  # Order matters, checks letters clockwise around the A
                find_letter(puzzle, rotation[0], i - 1, j - 1),
                find_letter(puzzle, rotation[1], i - 1, j + 1),
                find_letter(puzzle, rotation[2], i + 1, j + 1),
                find_letter(puzzle, rotation[3], i + 1, j - 1),
            ]
        )
        if is_x_mas:
            return True

    return False


def count_all_x_mas(puzzle: WordSearch) -> int:
    count = 0
    for i, row in enumerate(puzzle):
        for j, _ in enumerate(row):
            count += find_x_mas(puzzle, i, j)

    return count


if __name__ == '__main__':
    puzzle = parse_puzzle()
    print('Day 4, Part 1')
    with timer():
        result = count_all_xmas(puzzle)
    print(f'XMAS count: {result}\n')    # 2517

    print('Day 4, Part 2')
    with timer():
        result = count_all_x_mas(puzzle)
    print(f'Result: {result}\n')        # 1960
