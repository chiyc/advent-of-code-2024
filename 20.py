from __future__ import annotations

from collections import deque
from enum import Enum, auto
from typing import NamedTuple, NewType, Optional, Tuple

from lib import read_input, timer


class Pos(NamedTuple):
    i: int
    j: int

    def __add__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            return NotImplemented
        return Pos(self.i + other.i, self.j + other.j)

    def __repr__(self) -> str:
        return f'Pos({self.i}, {self.j})'

    def dist_taxi(self, other: Pos) -> int:
        return abs(other.j - self.j) + abs(other.i - self.i)


class Terrain(Enum):
    FLOOR = auto()
    WALL = auto()


class Map:
    def __init__(
        self,
        map_grid: list[list[Terrain]],
    ):
        self._grid = map_grid

    @property
    def rows(self) -> int:
        return len(self._grid)

    @property
    def cols(self) -> int:
        assert self.rows
        return len(self._grid[0])

    def __getitem__(self, pos: Pos) -> Terrain:
        return self._grid[pos.i][pos.j]


def parse_input() -> Tuple[Map, Pos, Pos]:
    input = read_input(20)
    start_pos: Optional[Pos] = None
    end_pos: Optional[Pos] = None
    map_grid: list[list[Terrain]] = []
    for i, line in enumerate(input):
        if 'S' in line:
            start_pos = Pos(i, line.index('S'))
        if 'E' in line:
            end_pos = Pos(i, line.index('E'))
        row = [Terrain.WALL if x == '#' else Terrain.FLOOR for x in line]
        map_grid.append(row)

    assert start_pos
    assert end_pos
    return (Map(map_grid), start_pos, end_pos)


Shortest = NewType('Shortest', dict[Pos, int])


def find_shortest_distance(map: Map, start: Pos, end: Pos) -> Shortest:
    shortest = Shortest({})
    next = deque([(start, 0)])
    while next:
        pos, distance = next.pop()

        if not 0 <= pos.i < map.rows or not 0 <= pos.j < map.cols:
            continue

        if map[pos] == Terrain.WALL:
            continue

        if pos not in shortest or distance < shortest[pos]:
            shortest[pos] = distance
        else:
            continue

        next.extendleft(
            [
                (pos + Pos(0, 1), distance + 1),
                (pos + Pos(0, -1), distance + 1),
                (pos + Pos(1, 0), distance + 1),
                (pos + Pos(-1, 0), distance + 1),
            ]
        )
    return shortest


class Segment(NamedTuple):
    start: Pos
    end: Pos


Shortcuts = NewType('Shortcuts', dict[Segment, int])


def find_shortcuts(shortest: Shortest, max_steps: int) -> Shortcuts:
    cuts = get_cuts(max_steps)

    shortcuts = Shortcuts({})
    for end, distance in shortest.items():
        for cut in cuts:
            start = end + cut
            steps = end.dist_taxi(start)
            ps_saved = shortest.get(start, 0) - distance - steps
            if ps_saved > 0:
                shortcuts[Segment(start, end)] = ps_saved

    return shortcuts


def get_cuts(steps: int) -> set[Pos]:
    cuts = set()
    next = deque([(Pos(0, 0), steps)])
    while next:
        pos, remaining = next.pop()

        if pos in cuts:
            continue

        if remaining < steps:
            cuts.add(pos)

        if remaining == 0:
            continue

        next.extendleft(
            [
                (pos + Pos(0, 1), remaining - 1),
                (pos + Pos(0, -1), remaining - 1),
                (pos + Pos(1, 0), remaining - 1),
                (pos + Pos(-1, 0), remaining - 1),
            ]
        )

    return cuts


if __name__ == '__main__':
    map, start, end = parse_input()

    print('Day 20, Part 1')
    with timer():
        shortest = find_shortest_distance(map, end, start)
        shortcuts = find_shortcuts(shortest, 2)
        result = sum(1 for d in shortcuts.values() if d >= 100)
    print(f'Result: {result}\n')    # 1263

    print('Day 20, Part 2')
    with timer():
        shortcuts = find_shortcuts(shortest, 20)
        result = sum(1 for d in shortcuts.values() if d >= 100)
    print(f'Result: {result}\n')    # 957831
