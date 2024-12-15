from __future__ import annotations

from collections import deque
from enum import Enum, auto
from typing import (
    Iterable,
    Literal,
    NamedTuple,
    NewType,
    Optional,
    Tuple,
    Union,
)

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


Box = NewType('Box', Tuple[Pos, ...])


class Terrain(Enum):
    FLOOR = auto()
    WALL = auto()


class Map:
    def __init__(self, map_grid: list[list[Terrain]], boxes: set[Box]):
        self._grid = map_grid
        self._boxes = boxes

    def get_box(self, pos: Pos) -> Optional[Box]:
        possible_boxes = [
            Box(tuple((pos,))),
            Box(tuple((pos - Pos(0, 1), pos))),
            Box(tuple((pos, pos + Pos(0, 1)))),
        ]
        for box in possible_boxes:
            if box in self._boxes:
                return box
        return None

    def free_to_move(self, start: Pos, dir: Pos) -> Optional[list[Box]]:
        boxes_to_move: dict[Box, Literal[True]] = {}

        next: deque[list[Pos]] = deque([[start + dir]])
        while next:
            positions = next.pop()
            if any(self._grid[p.i][p.j] == Terrain.WALL for p in positions):
                return None

            boxes: set[Box] = set()
            for pos in positions:
                box = self.get_box(pos)
                if box is not None:
                    boxes.add(box)

            for box in boxes:
                boxes_to_move[box] = True
                if dir in [Pos(1, 0), Pos(-1, 0)]:
                    next.appendleft([pos + dir for pos in box])
                elif dir == Pos(0, 1):
                    next.appendleft([box[-1] + dir])
                elif dir == Pos(0, -1):
                    next.appendleft([box[0] + dir])
                else:
                    assert False

        return list(boxes_to_move.keys())

    def move_box(self, box: Box, dir: Pos) -> None:
        next_spaces = tuple(pos + dir for pos in box)
        if any(
            self._grid[next.i][next.j] == Terrain.WALL for next in next_spaces
        ):
            raise Exception('Cannot move box {box} into wall')

        self._boxes.remove(box)
        next_box = Box(next_spaces)
        if next_box in self._boxes:
            self._boxes.add(box)
            raise Exception('Cannot move box {box} to {next}')
        self._boxes.add(next_box)

    def get_boxes_coordinates(self) -> Iterable[Pos]:
        return [box[0] for box in self._boxes]

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
                elif x == 'O':
                    boxes.add(
                        Box(tuple(Pos(i, len(row) + w) for w in range(width)))
                    )
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

            free_to_move = self.map.free_to_move(self.robot.pos, dir)
            if free_to_move is None:
                continue

            for box in reversed(free_to_move):
                self.map.move_box(box, dir)

            self.robot.pos += dir
        return None

    def sum_gps_coordinates(self) -> int:
        return sum(
            pos.i * 100 + pos.j for pos in self.map.get_boxes_coordinates()
        )


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
    print(f'Result: {result}\n')    # 1472235
