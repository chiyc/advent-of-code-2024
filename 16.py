from __future__ import annotations

from collections import deque
from enum import Enum, auto
from typing import Iterable, NamedTuple, NewType, Tuple, Union

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
    def __init__(self, map_grid: list[list[Terrain]]):
        self._grid = map_grid

    def __getitem__(self, pos: Pos) -> Terrain:
        return self._grid[pos.i][pos.j]


def parse_input(input: Iterable[str]) -> Tuple[Map, Reindeer, Pos]:
    map_grid: list[list[Terrain]] = []
    reindeer_pos: Union[None, Pos] = None
    end_pos: Union[None, Pos] = None
    for i, line in enumerate(input):
        if 'S' in line:
            reindeer_pos = Pos(i, line.index('S'))
        if 'E' in line:
            end_pos = Pos(i, line.index('E'))
        row = [Terrain.WALL if x == '#' else Terrain.FLOOR for x in line]
        map_grid.append(row)

    assert len(map_grid) and len(map_grid[0])
    assert reindeer_pos
    assert end_pos
    return (Map(map_grid), Reindeer(reindeer_pos, Pos(0, 1)), end_pos)


Scores = NewType('Scores', dict[Reindeer, int])

Paths = NewType('Paths', dict[Reindeer, list[list[Reindeer]]])


def find_best_path(map: Map, reindeer: Reindeer) -> Tuple[Scores, Paths]:
    scores: Scores = Scores({})
    best_paths: Paths = Paths({})

    next: deque[Tuple[Reindeer, list[Reindeer], int]] = deque(
        [(reindeer, [], 0)]
    )
    while next:
        reindeer, prev_path, score = next.pop()

        path = prev_path + [reindeer]

        if reindeer not in scores or score < scores[reindeer]:
            scores[reindeer] = score
            best_paths[reindeer] = [path]
        elif score == scores[reindeer]:
            best_paths[reindeer].append(path)
            continue
        else:
            continue

        pos, facing = reindeer

        if map[pos] == Terrain.WALL:
            continue

        next_reindeer = [
            (Reindeer(pos + facing, facing), path, score + 1),
            (
                Reindeer(pos, turn_reindeer(facing, reverse=False)),
                path,
                score + 1000,
            ),
            (
                Reindeer(pos, turn_reindeer(facing, reverse=True)),
                path,
                score + 1000,
            ),
        ]
        next.extendleft(next_reindeer)
    return scores, best_paths


def best_score(scores: Scores, end_pos: Pos) -> int:
    end_scores = []
    for turn in TURNS:
        end = Reindeer(end_pos, turn)
        if end in scores:
            end_scores.append(scores[end])
    return min(end_scores)


def best_path_positions(best_paths: Paths, end_pos: Pos) -> set[Pos]:
    end_reindeers = [
        Reindeer(end_pos, turn)
        for turn in TURNS
        if Reindeer(end_pos, turn) in best_paths
    ]

    visited: set[Reindeer] = set()
    next = deque([reindeer for reindeer in end_reindeers])
    while next:
        reindeer = next.pop()
        if reindeer in visited:
            continue
        visited.add(reindeer)

        paths = best_paths[reindeer]
        next.extendleft(
            path[-2] if len(path) > 1 else path[0] for path in paths
        )

    return set(reindeer.pos for reindeer in visited)


if __name__ == '__main__':
    map, reindeer, end = parse_input(read_input(16))

    print('Day 16, Part 1')
    with timer():
        scores, paths = find_best_path(map, reindeer)
        result = best_score(scores, end)
    print(f'Result: {result}\n')    # 74392

    print('Day 16, Part 2')
    with timer():
        result = len(best_path_positions(paths, end))
    print(f'Result: {result}\n')    # 426
