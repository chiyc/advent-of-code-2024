from __future__ import annotations

from typing import Callable, NamedTuple, NewType, TypeAliasType

from lib import read_input, timer


TrailMap = NewType('TrailMap', list[list[int]])
Tile = NewType('Tile', int)


class Pos(NamedTuple):
    i: int
    j: int

    def __add__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            raise NotImplemented
        return Pos(self.i + other.i, self.j + other.j)


def parse_trail_map() -> TrailMap:
    return TrailMap(
        [[Tile(int(n)) for n in str(line)] for line in read_input(10)]
    )


def blaze_trailhead(trail_map: TrailMap, start: Pos) -> list[Pos]:
    MAX_ROW = len(trail_map) - 1
    MAX_COL = len(trail_map[0]) - 1

    def blaze_trail(pos: Pos, prev_height: int) -> list[Pos]:
        if not 0 <= pos.i <= MAX_ROW or not 0 <= pos.j <= MAX_COL:
            return []

        height = trail_map[pos.i][pos.j]
        if height != prev_height + 1:
            return []

        if trail_map[pos.i][pos.j] == 9:
            return [pos]

        next = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0)]
        return [
            summit
            for step in next
            for summit in blaze_trail(pos + step, height)
        ]

    return blaze_trail(start, -1)


Scorer = TypeAliasType('Scorer', Callable[[list[Pos]], int])


def score_trailheads(trail_map: TrailMap, score: Scorer) -> int:
    total = 0
    for i, row in enumerate(trail_map):
        for j, height in enumerate(row):
            if height == 0:
                total += score(blaze_trailhead(trail_map, Pos(i, j)))
    return total


if __name__ == '__main__':
    trail_map = parse_trail_map()

    print('Day 10, Part 1')
    with timer():
        result = score_trailheads(trail_map, lambda summits: len(set(summits)))
    print(f'Result: {result}\n')    # 587

    print('Day 10, Part 2')
    with timer():
        result = score_trailheads(trail_map, lambda summits: len(summits))
    print(f'Result: {result}\n')    # 1340
