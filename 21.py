from __future__ import annotations

from collections import deque
from typing import Iterable, NamedTuple, NewType, Tuple

from lib import read_input, timer


class Pos(NamedTuple):
    i: int
    j: int

    def __add__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            return NotImplemented
        return Pos(self.i + other.i, self.j + other.j)

    def __sub__(self, other: object) -> Pos:
        if not isinstance(other, Pos):
            return NotImplemented
        return Pos(self.i - other.i, self.j - other.j)

    def __repr__(self) -> str:
        return f'Pos({self.i}, {self.j})'

    def dist_taxi(self, other: Pos) -> int:
        return abs(other.j - self.j) + abs(other.i - self.i)


Code = NewType('Code', list[str])


def parse_input() -> Iterable[Code]:
    input = read_input(21)
    return [Code(list(line)) for line in input]


Pad = NewType('Pad', list[list[str]])


KEYPAD = Pad(
    [
        ['7', '8', '9'],
        ['4', '5', '6'],
        ['1', '2', '3'],
        ['#', '0', 'A'],
    ]
)

DIRPAD = Pad(
    [
        ['#', '^', 'A'],
        ['<', 'v', '>'],
    ]
)

DIR_KEY = {
    Pos(0, 1): '>',
    Pos(0, -1): '<',
    Pos(1, 0): 'v',
    Pos(-1, 0): '^',
}

DIRS = DIR_KEY.keys()


Path = NewType('Path', list[Pos])


def path_button_positions(pad: Pad, start: Pos, end: Pos) -> list[list[str]]:
    shortest_paths: list[Path] = []

    next: deque[Tuple[Pos, Path]] = deque([(start, Path([]))])
    while next:
        pos, path = next.pop()

        if not 0 <= pos.i < len(pad) or not 0 <= pos.j < len(pad[0]):
            continue

        button = pad[pos.i][pos.j]

        if button == '#':
            continue

        if pos in path:
            continue

        next_path = Path(path + [pos])
        if pos == end and not shortest_paths:
            shortest_paths = [next_path]
            continue
        elif pos == end and len(next_path) < len(shortest_paths[0]):
            shortest_paths = [next_path]
            continue
        elif pos == end and len(next_path) == len(shortest_paths[0]):
            shortest_paths.append(next_path)
            continue

        next.extendleft((pos + dir, next_path) for dir in DIRS)

    return [
        [DIR_KEY[dir] for dir in get_path_dirs(path)] + ['A']
        for path in shortest_paths
    ]


def get_path_dirs(path: Path) -> list[Pos]:
    return [pos - prev for prev, pos in zip(path, path[1:])]


def prune_combos(combos: list[list[str]]) -> list[list[str]]:
    lengths = [len(combo) for combo in combos]
    min_length = min(lengths)
    return [c for c in combos if len(c) == min_length]


def shortest_combo(combos: list[list[str]]) -> list[str]:
    return prune_combos(combos)[0]


def get_dirpad_press_combos(pad: Pad, buttons: list[str]) -> list[list[str]]:
    pad_pos = {
        key: Pos(i, j)
        for i, row in enumerate(pad)
        for j, key in enumerate(row)
    }
    start_pos = pad_pos['A']

    press_combos: list[list[str]] = [[]]

    pos = start_pos
    for button in buttons:
        button_pos = pad_pos[button]

        paths = path_button_positions(pad, pos, button_pos)
        press_combos = [
            combo + path for path in paths for combo in press_combos
        ]

        pos = button_pos

    return prune_combos(press_combos)


def get_button_sequence(code: Code) -> list[str]:
    robot_keypad_combos = get_dirpad_press_combos(KEYPAD, code)

    robot_dirpad_combos = [
        dir_combo
        for key_combo in robot_keypad_combos
        for dir_combo in get_dirpad_press_combos(DIRPAD, key_combo)
    ]

    human_dirpad_combos = [
        human_combo
        for dir_combo in robot_dirpad_combos
        for human_combo in get_dirpad_press_combos(DIRPAD, dir_combo)
    ]

    return shortest_combo(human_dirpad_combos)


def complexity(code: Code, sequence: list[str]) -> int:
    number = int(''.join(code[:3]))
    sequence_length = len(sequence)
    score = number * sequence_length
    return score


if __name__ == '__main__':
    codes = parse_input()

    print('Day 21, Part 1')
    with timer():
        result = sum(
            complexity(code, get_button_sequence(code)) for code in codes
        )
    print(f'Result: {result}\n')    # 248108

    print('Day 21, Part 2')
    with timer():
        result = 0
    print(f'Result: {result}\n')    # 0
