from __future__ import annotations

from collections import deque
from typing import Iterator, NewType, Tuple

from lib import read_input, timer


Designs = NewType('Designs', list[str])


class Patterns:
    def __init__(self, patterns: set[str]):
        self._patterns = patterns
        self._max_length = max(len(p) for p in patterns)

    def starting(self, design: str) -> Iterator[str]:
        end = min(len(design), self._max_length)
        for i in reversed(range(1, end + 1)):
            if design[:i] in self._patterns:
                yield design[:i]


def parse_input() -> Tuple[Patterns, Designs]:
    input: Iterator[str] = read_input(19)

    raw_patterns: str = next(input)
    patterns = set(raw_patterns.split(', '))

    next(input)
    designs = [line for line in input]

    return Patterns(patterns), Designs(designs)


impossible_designs = set()


def match_design(patterns: Patterns, design: str) -> bool:
    if design == '':
        return True

    if design in impossible_designs:
        return False

    for pattern in patterns.starting(design):
        matches = match_design(patterns, design[len(pattern) :])
        if matches:
            return True

    impossible_designs.add(design)
    return False


design_variations: dict[str, int] = {}


def count_design_variations_slowly(patterns: Patterns, design: str) -> int:
    if design in design_variations:
        return design_variations[design]

    count = 0
    seen = set()

    next_designs: deque[Tuple[Tuple[str, ...], str]] = deque(
        [(tuple(), design)]
    )
    while next_designs:
        current = next_designs.pop()
        variation, remaining = current
        if remaining == '':
            count += 1
            continue

        if remaining in impossible_designs:
            continue

        if remaining in design_variations:
            count += design_variations[remaining]
            continue

        if current in seen:
            continue
        seen.add(current)

        next_designs.extendleft(
            (variation + (pattern,), remaining[len(pattern) :])
            for pattern in patterns.starting(remaining)
        )

    design_variations[design] = count
    return count


def count_design_variations(patterns: Patterns, design: str) -> int:
    if design == '':
        return 1

    if design in impossible_designs:
        return 0

    if design in design_variations:
        return design_variations[design]

    variations = 0
    for i in reversed(range(len(design))):
        right = design[i:]
        variations = count_design_variations_slowly(patterns, right)

    return variations


def match_designs(patterns: Patterns, designs: Designs) -> int:
    return sum(match_design(patterns, design) for design in designs)


def count_designs(patterns: Patterns, designs: Designs) -> int:
    return sum(count_design_variations(patterns, design) for design in designs)


if __name__ == '__main__':
    patterns, designs = parse_input()

    print('Day 19, Part 1')
    with timer():
        result = match_designs(patterns, designs)
    print(f'Result: {result}\n')    # 287

    print('Day 19, Part 2')
    with timer():
        result = count_designs(patterns, designs)
    print(f'Result: {result}\n')    # 571894474468161
