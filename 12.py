from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import NamedTuple, NewType

from lib import read_input, timer


Tile = NewType('Tile', str)
Map = NewType('Map', list[list[Tile]])


class Pos(NamedTuple):
    i: int
    j: int

    def __add__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            raise NotImplemented
        return Pos(self.i + other.i, self.j + other.j)


def parse_map() -> Map:
    return Map([[Tile(c) for c in list(line)] for line in read_input(12)])


@dataclass
class Region:
    type: Tile
    positions: set[Pos]
    perimeter: int


def find_regions(map: Map) -> list[Region]:
    MAX_ROW = len(map) - 1
    MAX_COL = len(map[0]) - 1

    def visit_region(start: Pos) -> Region:
        region = Region(
            type=map[start.i][start.j],
            positions=set(),
            perimeter=0,
        )

        visited: set[Pos] = set()
        next = deque([start])
        while next:
            pos = next.pop()
            if not 0 <= pos.i <= MAX_ROW or not 0 <= pos.j <= MAX_COL:
                region.perimeter += 1
                continue

            if map[pos.i][pos.j] != region.type:
                region.perimeter += 1
                continue

            if pos in visited:
                continue
            visited.add(pos)

            region.positions.add(pos)
            next_steps = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0)]
            next.extendleft(pos + step for step in next_steps)

        return region

    regions: list[Region] = []

    visited: set[Pos] = set()
    for i, row in enumerate(map):
        for j, _ in enumerate(row):
            pos = Pos(i, j)
            if pos not in visited:
                region = visit_region(pos)
                visited.update(region.positions)
                regions.append(region)

    return regions


def sum_fence_costs(regions: list[Region]) -> int:
    return sum(len(region.positions) * region.perimeter for region in regions)


if __name__ == '__main__':
    map = parse_map()
    assert len(map)
    assert len(map[0])

    print('Day 12, Part 1')
    with timer():
        regions = find_regions(map)
        result = sum_fence_costs(regions)
    print(f'Result: {result}\n')    # 1370258

    print('Day 12, Part 2')
    with timer():
        result = 0
    print(f'Result: {result}\n')    #
