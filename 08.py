from __future__ import annotations
import itertools

from collections import defaultdict
from typing import NamedTuple

from lib import read_input, timer


class Pos(NamedTuple):
    i: int
    j: int

    def __add__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            raise NotImplemented
        return Pos(self.i + other.i, self.j + other.j)

    def __sub__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            raise NotImplemented
        return Pos(self.i - other.i, self.j - other.j)


def parse_map() -> list[list[str]]:
    return [list(line) for line in read_input(8)]


def get_satellite_positions(map: list[list[str]]) -> dict[str, list[Pos]]:
    assert len(map)
    assert len(map[0])

    satellite_positions = defaultdict(list)
    for i, line in enumerate(map):
        for j, c in enumerate(line):
            if c != '.':
                satellite_positions[c].append(Pos(i, j))

    return satellite_positions


def calculate_pair_antinodes(
    a: Pos, b: Pos, max_row: int, max_col: int
) -> list[Pos]:
    delta = b - a
    antinodes = [
        b + delta,
        a - delta,
    ]
    return [
        pos
        for pos in antinodes
        if 0 <= pos.i <= max_row and 0 <= pos.j <= max_col
    ]


def calculate_resonant_antinodes(
    a: Pos, b: Pos, max_row: int, max_col: int
) -> list[Pos]:
    delta = b - a
    antinodes = []

    next = b + delta
    while 0 <= next.i <= max_row and 0 <= next.j <= max_col:
        antinodes.append(next)
        next += delta

    next = a - delta
    while 0 <= next.i <= max_row and 0 <= next.j <= max_col:
        antinodes.append(next)
        next -= delta

    return antinodes


def calculate_antinodes(
    positions: list[Pos], max_row: int, max_col: int, resonant: bool
) -> list[Pos]:
    antinodes = []
    for a, b in itertools.combinations(positions, 2):
        more_antinodes = (
            calculate_resonant_antinodes(a, b, max_row, max_col)
            if resonant
            else calculate_pair_antinodes(a, b, max_row, max_col)
        )
        if resonant and len(positions) > 2:
            more_antinodes.extend(positions)

        antinodes.extend(more_antinodes)

    return antinodes


def count_unique_antinodes(
    satellite_positions: dict[str, list[Pos]],
    max_row: int,
    max_col: int,
    resonant: bool = False,
) -> int:
    antinodes: set[Pos] = set()
    for _satellite, positions in satellite_positions.items():
        satellite_antinodes = calculate_antinodes(
            positions, max_row, max_col, resonant
        )
        antinodes.update(satellite_antinodes)

    return len(antinodes)


if __name__ == '__main__':
    map = parse_map()
    satellite_positions = get_satellite_positions(map)
    max_row = len(map) - 1
    max_col = len(map[0]) - 1

    print('Day 8, Part 1')
    with timer():
        result = count_unique_antinodes(satellite_positions, max_row, max_col)
    print(f'Result: {result}\n')    # 285

    print('Day 8, Part 2')
    with timer():
        result = count_unique_antinodes(
            satellite_positions, max_row, max_col, resonant=True
        )
    print(f'Result: {result}\n')    # 944
