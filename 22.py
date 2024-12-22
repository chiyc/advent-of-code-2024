from __future__ import annotations

from typing import NewType, Tuple

from lib import read_input, timer


def parse_input() -> list[int]:
    return [int(n) for n in read_input(22)]


def next_secret(initial_secret: int) -> int:
    secret = initial_secret ^ (initial_secret * 64)
    secret = secret % 16777216

    secret = secret ^ (secret // 32)
    secret = secret % 16777216

    secret = secret ^ (secret * 2048)
    secret = secret % 16777216
    return secret


def nth_secret(secret: int, n: int) -> int:
    for _ in range(n):
        secret = next_secret(secret)
    return secret


Sequence = NewType('Sequence', Tuple[int, int, int, int])


def sequence_prices(initial_secret: int, n: int) -> dict[Sequence, int]:
    sequence_prices: dict[Sequence, int] = {}

    sequence = []
    prev_secret = initial_secret
    for _ in range(n):
        prev_price = prev_secret % 10

        curr = next_secret(prev_secret)
        curr_price = curr % 10

        sequence.append(curr_price - prev_price)

        if len(sequence) >= 4:
            sequence_tuple = Sequence(
                (
                    sequence[-4],
                    sequence[-3],
                    sequence[-2],
                    sequence[-1],
                )
            )
            if sequence_tuple not in sequence_prices:
                sequence_prices[sequence_tuple] = curr_price

        prev_secret = curr

    return sequence_prices


def maximize_bananas(secrets: list[int]) -> int:
    sequences_list = [sequence_prices(s, 2000) for s in secrets]
    sequences = set(k for s in sequences_list for k in set(s.keys()))
    max_bananas = max(
        sum(s.get(sequence, 0) for s in sequences_list)
        for sequence in sequences
    )
    return max_bananas


if __name__ == '__main__':
    initial_secrets = parse_input()

    print('Day 22, Part 1')
    with timer():
        result = sum(nth_secret(secret, 2000) for secret in initial_secrets)
    print(f'Result: {result}\n')    # 13004408787

    print('Day 22, Part 2')
    with timer():
        result = maximize_bananas(initial_secrets)
    print(f'Result: {result}\n')    # 1455
