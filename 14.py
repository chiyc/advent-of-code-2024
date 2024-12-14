from __future__ import annotations
import math
import re

from collections import defaultdict
from typing import NamedTuple

from lib import read_input, timer


class Vec(NamedTuple):
    x: int
    y: int

    def __add__(self, other: object) -> Vec:
        if not isinstance(other, Vec):
            raise NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

    def __mul__(self, other: object) -> Vec:
        if not isinstance(other, int):
            raise NotImplemented
        return Vec(self.x * other, self.y * other)


class Robot(NamedTuple):
    start: Vec
    vel: Vec


def parse_robots() -> dict[Robot, Vec]:
    PATTERN = r'p=(?P<px>\d+),(?P<py>\d+) v=(?P<vx>-?\d+),(?P<vy>-?\d+)'

    robots = {}
    for line in read_input(14):
        m = re.match(PATTERN, line)
        assert m
        px, py, vx, vy = map(int, m.group('px', 'py', 'vx', 'vy'))
        robot = Robot(Vec(px, py), Vec(vx, vy))
        robots[robot] = robot.start

    return robots


ROWS = 103
COLS = 101


def predict_robots(robots: dict[Robot, Vec], seconds: int) -> dict[Robot, Vec]:
    robot_positions = {}
    for robot, pos in robots.items():
        new_pos = pos + robot.vel * seconds
        wrapped = Vec(new_pos.x % COLS, new_pos.y % ROWS)
        robot_positions[robot] = wrapped
    return robot_positions


def count_quadrants(robot_positions: dict[Robot, Vec]) -> dict[int, int]:
    middle_row = ROWS // 2
    middle_col = COLS // 2

    quadrant_count: dict[int, int] = defaultdict(int)
    for pos in robot_positions.values():
        if pos.x > middle_col and pos.y < middle_row:
            quadrant_count[1] += 1
        elif pos.x < middle_col and pos.y < middle_row:
            quadrant_count[2] += 1
        elif pos.x < middle_col and pos.y > middle_row:
            quadrant_count[3] += 1
        elif pos.x > middle_col and pos.y > middle_row:
            quadrant_count[4] += 1

    return quadrant_count


def score_safety(robot_positions: dict[Robot, Vec]) -> int:
    quadrant_count = count_quadrants(robot_positions)
    return math.prod(quadrant_count.values())


def print_robot_positions(robot_positions: dict[Robot, Vec]) -> str:
    grid = [[0] * COLS for _ in range(ROWS)]
    for pos in robot_positions.values():
        grid[pos.y][pos.x] += 1

    def symbol(n: int) -> str:
        if n == 0:
            return '.'
        elif n < 10:
            return str(n)
        else:
            return chr(n + 55)

    rows = []
    for row in grid:
        rows.append(''.join(symbol(n) for n in row))

    return '\n'.join(rows)


if __name__ == '__main__':
    robots = parse_robots()
    start = print_robot_positions(robots)

    print('Day 14, Part 1')
    with timer():
        positions = predict_robots(robots, 100)
        result = score_safety(positions)
    print(f'Result: {result}\n')    # 231852216

    print('Day 14, Part 2')
    with timer():
        safety_for_seconds = []
        seconds = 1
        while True:
            positions = predict_robots(robots, seconds)
            safety = score_safety(positions)
            position_str = print_robot_positions(positions)
            safety_for_seconds.append((seconds, safety, position_str))
            if position_str == start:   # This might be a loop
                # 10403 seconds (too high)
                break
            seconds += 1
        safety_for_seconds.sort(key=lambda v: v[1])
        result = safety_for_seconds[0][0]
    print(f'Result: {result}\n')  # 8159
    print(safety_for_seconds[0][2])
