from __future__ import annotations
import bisect
import sys

from collections import deque
from enum import Enum, auto
from typing import Iterable, NamedTuple, NewType, Optional, Tuple

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


class Reindeer(NamedTuple):
    pos: Pos
    facing: Pos


TURNS = [Pos(-1, 0), Pos(0, 1), Pos(1, 0), Pos(0, -1)]


def turn_reindeer(facing: Pos, reverse: bool = False) -> Pos:
    step = -1 if reverse else 1
    current_facing = TURNS.index(facing)
    next_facing = (current_facing + step) % len(TURNS)
    return TURNS[next_facing]


def next_turns(facing: Pos) -> list[Pos]:
    return [
        turn_reindeer(facing, reverse=False),
        turn_reindeer(facing, reverse=True),
    ]


class Terrain(Enum):
    FLOOR = auto()
    WALL = auto()


class Map:
    def __init__(
        self,
        map_grid: list[list[Terrain]],
        obstacles: Optional[set[Pos]] = None,
    ):
        self._grid = map_grid
        self._obstacles = set() if obstacles is None else obstacles

    def add_obstacles(self, obstacles: Iterable[Pos]) -> None:
        self._obstacles.update(obstacles)

    def with_obstacles(self, obstacles: Iterable[Pos]) -> Map:
        self._obstacles = set(obstacles)
        return self

    def __getitem__(self, pos: Pos) -> Terrain:
        return (
            Terrain.WALL
            if pos in self._obstacles
            else self._grid[pos.i][pos.j]
        )


ROWS, COLS = 71, 71


def parse_input() -> Tuple[Map, list[Pos]]:
    map_grid: list[list[Terrain]] = [
        [Terrain.FLOOR for _ in range(COLS)] for _ in range(ROWS)
    ]
    obstacles = []
    for line in read_input(18):
        x, y = line.split(',')
        obstacles.append(Pos(int(y), int(x)))

    return (Map(map_grid), obstacles)


Shortest = NewType('Shortest', dict[Pos, int])


EXIT = Pos(ROWS - 1, COLS - 1)


def find_shortest_distance(map: Map) -> Shortest:
    START = Pos(0, 0)

    shortest = Shortest({})
    next = deque([(START, 0)])
    while next:
        pos, distance = next.pop()

        if pos not in shortest or distance < shortest[pos]:
            shortest[pos] = distance
        else:
            continue

        if not 0 <= pos.i <= ROWS - 1 or not 0 <= pos.j <= COLS - 1:
            continue

        if map[pos] == Terrain.WALL:
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


if __name__ == '__main__':
    map, obstacles = parse_input()

    print('Day 16, Part 1')
    with timer():
        map.add_obstacles(obstacles[:1024])
        shortest_distance = find_shortest_distance(map)
        part1_result = shortest_distance[EXIT]
    print(f'Result: {part1_result}\n')    # 246

    print('Day 16, Part 2')
    with timer():
        byte = bisect.bisect_left(
            [i for i in range(len(obstacles))],
            x=sys.maxsize,
            lo=1024,
            hi=len(obstacles),
            key=lambda mid: find_shortest_distance(
                map.with_obstacles(obstacles[:mid])
            ).get(EXIT, sys.maxsize),
        )
        last_byte = obstacles[byte - 1]
        part2_result = f'{last_byte.j},{last_byte.i}'
    print(f'Result: {part2_result}\n')    # 22,50
