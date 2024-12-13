import re

from typing import NamedTuple, Optional, Tuple, TypedDict, Union

from lib import read_input, timer


class Vec(NamedTuple):
    x: int
    y: int


class Machine(TypedDict):
    A: Vec
    B: Vec
    Prize: Vec


PATTERN = r'Button A: X\+(?P<AX>\d+), Y\+(?P<AY>\d+)\nButton B: X\+(?P<BX>\d+), Y\+(?P<BY>\d+)\nPrize: X=(?P<X>\d+), Y=(?P<Y>\d+)'


def parse_machines() -> list[Machine]:
    machines: list[Machine] = []

    full_input = '\n'.join(read_input(13))
    matches = re.finditer(PATTERN, full_input, re.MULTILINE)
    for m in matches:
        ax, ay, bx, by, x, y = map(
            int, m.group('AX', 'AY', 'BX', 'BY', 'X', 'Y')
        )
        machine: Machine = {
            'A': Vec(ax, ay),
            'B': Vec(bx, by),
            'Prize': Vec(x, y),
        }
        machines.append(machine)

    return machines


def solve_presses(machine: Machine) -> Tuple[Optional[int], Optional[int]]:
    ax, ay = machine['A']
    bx, by = machine['B']
    x, y = machine['Prize']

    num = ax * y - ay * x
    denom = ax * by - ay * bx
    b_presses = num // denom
    if b_presses * denom != num:
        return (None, None)

    num = x - bx * b_presses
    a_presses = num // ax
    if a_presses * ax != num:
        return (None, None)

    return (a_presses, b_presses)


A_TOKENS, B_TOKENS = 3, 1


def total_prizes_cost(machines: list[Machine]) -> int:
    tokens = 0
    for machine in machines:
        a, b = solve_presses(machine)
        if a is not None and b is not None:
            tokens += A_TOKENS * a + B_TOKENS * b

    return tokens


def total_prizes_cost_with_conversion(machines: list[Machine]) -> int:
    tokens = 0
    for machine in machines:
        x, y = machine['Prize']
        a, b = solve_presses(
            {**machine, 'Prize': Vec(10000000000000 + x, 10000000000000 + y)}
        )
        if a is not None and b is not None:
            tokens += A_TOKENS * a + B_TOKENS * b

    return tokens


if __name__ == '__main__':
    machines = parse_machines()

    print('Day 13, Part 1')
    with timer():
        result = total_prizes_cost(machines)
    print(f'Result: {result}\n')    # 33209

    print('Day 13, Part 2')
    with timer():
        result = total_prizes_cost_with_conversion(machines)
    print(f'Result: {result}\n')    # 83102355665474
