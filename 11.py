from __future__ import annotations

from collections import Counter
from typing import TypeAliasType

from lib import read_input, timer


Stones = TypeAliasType('Stones', Counter[int])


def parse_stones() -> Stones:
    return Counter(int(n) for line in read_input(11) for n in line.split(' '))


def blink_once(stones: Stones) -> Stones:
    next_stones: Stones = Counter()

    for stone, count in stones.items():
        stone_text = str(stone)
        if stone == 0:
            next_stones[1] += count

        elif len(stone_text) % 2 == 0:
            midpoint = len(stone_text) // 2
            left = stone_text[:midpoint]
            right = stone_text[midpoint:]
            next_stones[int(left)] += count
            next_stones[int(right)] += count

        else:
            next_stones[stone * 2024] += count

    return next_stones


def blink(stones: Stones, times: int) -> Stones:
    for _ in range(times):
        stones = blink_once(stones)
    return stones


if __name__ == '__main__':
    stones = parse_stones()

    print('Day 11, Part 1')
    with timer():
        result = blink(stones, 25).total()
    print(f'Result: {result}\n')    # 187738

    print('Day 11, Part 2')
    with timer():
        result = blink(stones, 75).total()
    print(f'Result: {result}\n')    # 223767210249237
