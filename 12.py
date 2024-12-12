from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import NamedTuple, NewType, Tuple, TypeAliasType

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

    def __sub__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            raise NotImplemented
        return Pos(self.i - other.i, self.j - other.j)


def parse_map() -> Map:
    return Map([[Tile(c) for c in list(line)] for line in read_input(12)])


class Dir(Pos):
    pass


Fence = TypeAliasType('Fence', Tuple[Pos, Dir])


@dataclass
class Region:
    type: Tile
    positions: set[Pos]
    fences: list[Fence]


def find_regions(map: Map) -> list[Region]:
    MAX_ROW = len(map) - 1
    MAX_COL = len(map[0]) - 1

    def visit_region(start: Pos) -> Region:
        region = Region(type=map[start.i][start.j], positions=set(), fences=[])

        visited: set[Pos] = set()
        next: deque[Tuple[Pos, Pos]] = deque([(Pos(-1, -1), start)])
        while next:
            prev, pos = next.pop()
            dir = pos - prev
            dir = Dir(dir.i, dir.j)
            if not 0 <= pos.i <= MAX_ROW or not 0 <= pos.j <= MAX_COL:
                region.fences.append((prev, dir))
                continue

            if map[pos.i][pos.j] != region.type:
                region.fences.append((prev, dir))
                continue

            if pos in visited:
                continue
            visited.add(pos)

            region.positions.add(pos)
            next_steps = [Pos(0, 1), Pos(0, -1), Pos(1, 0), Pos(-1, 0)]
            next.extendleft((pos, pos + step) for step in next_steps)

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
    return sum(
        len(region.positions) * len(region.fences) for region in regions
    )


@dataclass
class FenceGroup:
    positions: list[Pos]
    next_dir: Pos


def region_sides(region: Region) -> int:
    """
    First, we group fence positions by the direction the fence faces.

    Then, we sort the positions in each group to enable easy checking
    of whether the next position is connected to the current side.
    """
    fence_groups: dict[Dir, FenceGroup] = {
        Dir(-1, 0): FenceGroup([], Pos(0, 1)),  # N face, sort so next is right
        Dir(1, 0): FenceGroup([], Pos(0, 1)),  # S face, sort so next is right
        Dir(0, 1): FenceGroup([], Pos(1, 0)),  # E face, sort so next is below
        Dir(0, -1): FenceGroup([], Pos(1, 0)),  # W face, sort so next is below
    }

    for pos, dir in region.fences:
        fence_groups[dir].positions.append(pos)

    sides = 0
    for group in fence_groups.values():
        i_sort = 1000**group.next_dir.j
        j_sort = 1000**group.next_dir.i
        group.positions.sort(key=lambda pos: pos.i * i_sort + pos.j * j_sort)

        sides += 1 + sum(
            1
            for prev, pos in zip(group.positions, group.positions[1:])
            if pos - prev != group.next_dir
        )

    return sides


def sum_bulk_fence_costs(regions: list[Region]) -> int:
    return sum(
        len(region.positions) * region_sides(region) for region in regions
    )


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
        regions = find_regions(map)
        result = sum_bulk_fence_costs(regions)
    print(f'Result: {result}\n')    # 805814
