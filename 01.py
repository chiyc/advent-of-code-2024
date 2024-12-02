from collections import Counter
from typing import Tuple

from lib import read_input, timer


def parse_lists() -> Tuple[list[int], list[int]]:
    list0 = []
    list1 = []

    for line in read_input(1):
        left, right = line.split('   ')
        list0.append(int(left))
        list1.append(int(right))

    return list0, list1


def part_1(list0: list[int], list1: list[int]) -> int:
    list0.sort()
    list1.sort()

    total_distance = sum([abs(n0 - n1) for n0, n1 in zip(list0, list1)])
    return total_distance


def part_2(list0: list[int], list1: list[int]) -> int:
    list1_counts = Counter(list1)
    return sum([n * list1_counts[n] for n in list0])


if __name__ == '__main__':
    list0, list1 = parse_lists()

    print('Day 1, Part 1')
    with timer():
        result = part_1(list0, list1)
    print(f'Total distance: {result}\n')  # 1834060

    print('Day 1, Part 2')
    with timer():
        result = part_2(list0, list1)
    print(f'Similarity score: {result}')  # 21607792
