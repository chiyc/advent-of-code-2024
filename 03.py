import re

from typing import Iterable

from lib import read_input, timer


def read_memory() -> list[str]:
    return list(read_input(3))


def find_mul_matches(memory: list[str]) -> Iterable[re.Match[str]]:
    PATTERN = r'(?P<instr>mul)\((?P<l>\d+),(?P<r>\d+)\)'

    matches: list[re.Match[str]] = []
    for line in memory:
        matches.extend(list(re.finditer(PATTERN, line)))
    return matches


def sum_mul_results(mul_matches: Iterable[re.Match[str]]) -> int:
    return sum(
        int(m.group('l')) * int(m.group('r'))
        for m in mul_matches
        if m.group('instr') == 'mul'
    )


def find_do_dont_mul_matches(memory: list[str]) -> Iterable[re.Match[str]]:
    PATTERN = r"(?P<instr>do|don't|mul)\(((?P<l>\d+),(?P<r>\d+))?\)"

    matches: list[re.Match[str]] = []
    for line in memory:
        matches.extend(list(re.finditer(PATTERN, line)))
    return matches


def sum_enabled_mul_results(
    instruction_matches: Iterable[re.Match[str]],
) -> int:
    result = 0

    enabled = True
    for m in instruction_matches:
        instr = m.group('instr')
        if enabled and instr == 'mul':
            result += int(m.group('l')) * int(m.group('r'))
        elif instr == 'do':
            enabled = True
        elif instr == "don't":
            enabled = False

    return result


if __name__ == '__main__':
    memory = read_memory()
    print('Day 3, Part 1')
    with timer():
        matches = find_mul_matches(memory)
        result = sum_mul_results(matches)
    print(f'Result: {result}\n')  # 179834255

    print('Day 3, Part 2')
    with timer():
        matches = find_do_dont_mul_matches(memory)
        result = sum_enabled_mul_results(matches)
    print(f'Result: {result}\n')  # 80570939
