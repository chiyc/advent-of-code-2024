from __future__ import annotations

from enum import Enum, auto
from typing import Iterable, Literal, NamedTuple, Optional, Union

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

    def __repr__(self) -> str:
        return f'Pos({self.i}, {self.j})'


class Command:
    U = Pos(-1, 0)
    D = Pos(1, 0)
    L = Pos(0, -1)
    R = Pos(0, 1)
    NOOP = Pos(0, 0)

    def __init__(self, c: str):
        self.move = c

    def execute(self) -> Pos:
        if self.move == '^':
            return Command.U
        elif self.move == 'v':
            return Command.D
        elif self.move == '<':
            return Command.L
        elif self.move == '>':
            return Command.R
        else:
            return Command.NOOP

    def __repr__(self) -> str:
        return f"Command('{self.move}')"


class Robot:
    def __init__(self, position: Pos):
        self.pos: Pos = position


class Terrain(Enum):
    FLOOR = auto()
    WALL = auto()


class Map:
    def __init__(self, map_grid: list[list[Terrain]], boxes: set[Pos]):
        self._grid = map_grid
        self._boxes = boxes

    def next_free(self, start: Pos, dir: Pos) -> Optional[Pos]:
        pos = start + dir
        tile = self._grid[pos.i][pos.j]
        while tile != Terrain.WALL:
            if pos not in self._boxes:
                return pos

            pos += dir
            tile = self._grid[pos.i][pos.j]

        return None

    def move_box(self, box: Pos, dir: Pos) -> None:
        next = box + dir
        if next in self._boxes or self._grid[next.i][next.j] == Terrain.WALL:
            raise Exception('Cannot move box in {box} to {next}')
        self._boxes.remove(box)
        self._boxes.add(next)

    @property
    def boxes(self) -> set[Pos]:
        return self._boxes

    @property
    def max_row(self) -> int:
        return len(self._grid) - 1

    @property
    def max_col(self) -> int:
        return len(self._grid[0]) - 1


class Warehouse:
    def __init__(self, map: Map, robot: Robot, commands: list[Command]):
        self.map = map
        self.robot = robot
        self.commands = commands

    @staticmethod
    def from_input_widened(input: Iterable[str]) -> Warehouse:
        return Warehouse.from_input(input, wide=True)

    @staticmethod
    def from_input(input: Iterable[str], wide: bool = False) -> Warehouse:
        width = 2 if wide else 1

        map_grid: list[list[Terrain]] = []
        boxes = set()
        robot_pos: Union[None, Pos] = None
        for i, line in enumerate(input):
            if line == '':
                break

            row: list[Terrain] = []
            for x in line:
                if x == '@':
                    robot_pos = Pos(i, len(row))
                    row.extend([Terrain.FLOOR] * width)
                elif x == 'O':  # TODO: Wide boxes
                    boxes.update([Pos(i, len(row) + w) for w in range(width)])
                    row.extend([Terrain.FLOOR] * width)
                elif x == '#':
                    row.extend([Terrain.WALL] * width)
                elif x == '.':
                    row.extend([Terrain.FLOOR] * width)
                else:
                    assert False
            map_grid.append(row)

        commands = [Command(c) for line in input for c in list(line)]

        assert len(map_grid) and len(map_grid[0])
        assert robot_pos
        return Warehouse(Map(map_grid, boxes), Robot(robot_pos), commands)

    def play(self) -> Union[Literal['EXIT'], None]:
        for command in self.commands:
            dir = command.execute()
            next_free = self.map.next_free(self.robot.pos, dir)
            if next_free is None:
                continue

            pos = next_free - dir
            while pos != self.robot.pos:
                self.map.move_box(pos, dir)
                pos -= dir
            self.robot.pos += dir
        return None

    def sum_gps_coordinates(self) -> int:
        return sum(i * 100 + j for i, j in self.map.boxes)


if __name__ == '__main__':
    print('Day 15, Part 1')
    with timer():
        world = Warehouse.from_input(read_input(15))
        world.play()
        result = world.sum_gps_coordinates()
    print(f'Result: {result}\n')    # 1448589

    print('Day 15, Part 2')
    with timer():
        world = Warehouse.from_input_widened(read_input(15))
        world.play()
        result = world.sum_gps_coordinates()
    print(f'Result: {result}\n')    #
