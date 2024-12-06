import copy

from collections import defaultdict
from typing import Iterable, Literal, NamedTuple, NewType, Self, Tuple, Union

from lib import read_input, timer


class Pos:
    i: int
    j: int

    def __init__(self, i, j):
        self.i = i
        self.j = j

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j

    def __hash__(self):
        return hash((self.i, self.j))

    def __add__(self, other: Self):
        return Pos(self.i + other.i, self.j + other.j)

    def __radd__(self, other: Self):
        return self.__add__(other)

    def __repr__(self):
        return f'Pos({self.i}, {self.j})'


class History(NamedTuple):
    position: Pos
    orientation: Pos


class Guard:
    orientations = [Pos(-1, 0), Pos(0, 1), Pos(1, 0), Pos(0, -1)]

    def __init__(self, position: Pos, facing: Pos):
        self.position: Pos = position
        self.orientation: Pos = facing
        self.history: set[History] = set()

    def next_position(self):
        return self.position + self.orientation

    def move(self, next_position: Pos):
        self.history.add(History(self.position, self.orientation))
        self.position = next_position

    def turn(self):
        current_orientation = Guard.orientations.index(self.orientation)
        next_orientation = (current_orientation + 1) % len(Guard.orientations)
        self.orientation = Guard.orientations[next_orientation]

    def has_looped(self):
        return History(self.position, self.orientation) in self.history


class Map:
    def __init__(self, map_grid: list[list[str]]):
        self._grid = map_grid
        self._obstacles: set[Pos] = set()

    def __len__(self):
        return len(self._grid)

    def __iter__(self):
        return (row for row in self._grid)

    def __getitem__(self, pos: Pos):
        if not 0 <= pos.i <= self.max_row or not 0 <= pos.j <= self.max_col:
            return ' '
        if pos in self._obstacles:
            return '#'
        return self._grid[pos.i][pos.j]

    @property
    def max_row(self):
        return len(self._grid) - 1

    @property
    def max_col(self):
        return len(self._grid[0]) - 1

    def reset(self):
        self._obstacles = set()

    def place_obstacle(self, pos: Pos):
        self._obstacles.add(pos)

    def contains(self, pos: Pos):
        return 0 <= pos.i <= self.max_row and 0 <= pos.j <= self.max_col


class World:
    def __init__(self, map: Map, guard: Guard):
        self.map = map
        self.starting_guard = copy.copy(guard)
        self.guard = guard

    @staticmethod
    def from_input(input: Iterable[str]):
        map_grid: list[list[str]] = []
        guard_pos: Union[None, Pos] = None
        for i, line in enumerate(input):
            row = list(line)
            map_grid.append(row)
            if '^' in row:
                guard_pos = Pos(i, row.index('^'))

        assert len(map_grid) and len(map_grid[0])
        assert guard_pos
        return World(Map(map_grid), Guard(guard_pos, Pos(-1, 0)))

    def play(self) -> Union[Literal['EXIT'], Literal['LOOP'], None]:
        while (
            self.map.contains(self.guard.position)
            and not self.guard.has_looped()
        ):
            next_pos = self.guard.next_position()
            if self.map[next_pos] == '#':
                self.guard.turn()
            else:
                self.guard.move(next_pos)

        if self.guard.has_looped():
            return 'LOOP'
        elif not self.map.contains(self.guard.position):
            return 'EXIT'
        else:
            return None

    def reset(self):
        self.map.reset()
        self.guard = Guard(
            self.starting_guard.position, self.starting_guard.orientation
        )

    def count_guard_positions(self) -> int:
        return len(set([history.position for history in self.guard.history]))

    def count_possible_loops(self) -> int:
        """
        Should be run after world.play() has run and guard position history exists
        """
        guard_position_history = set(
            history.position for history in self.guard.history
        )

        loops = 0
        for pos in guard_position_history:
            if pos != self.guard.position and self.map[pos] != '#':
                self.map.place_obstacle(pos)
            status = world.play()
            if status == 'LOOP':
                loops += 1
            world.reset()
        return loops


if __name__ == '__main__':
    world = World.from_input(read_input(6))

    print('Day 6, Part 1')
    with timer():
        world.play()
        result = world.count_guard_positions()
    print(f'Result: {result}\n')    # 5318

    print('Day 6, Part 2')
    with timer():   # Takes about 30 seconds to run
        result = world.count_possible_loops()
    print(f'Result: {result}\n')    # 1831
