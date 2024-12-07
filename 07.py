import functools
import math

from typing import Callable, Iterable, NamedTuple, Tuple, TypeAliasType

from lib import read_input, timer


class Equation(NamedTuple):
    total: int
    nums: list[int]


def parse_equations() -> list[Equation]:
    equations = []
    for line in read_input(7):
        raw_total, raw_numbers = line.split(': ')
        equations.append(
            Equation(int(raw_total), [int(n) for n in raw_numbers.split(' ')])
        )
    return equations


Operators = TypeAliasType(
    'Operators', Tuple[Callable[[Iterable[int]], int], ...]
)


def operator_combinations(
    operators: Operators, length: int
) -> Iterable[Operators]:
    def combination_helper(
        combinations: Iterable[Operators], remaining: int
    ) -> Iterable[Operators]:
        if not remaining:
            return combinations

        next_combinations = [
            combo + (op,) for op in operators for combo in combinations
        ]
        return combination_helper(next_combinations, remaining - 1)

    return combination_helper([(sum,)], length - 1)


def test_equation(equation: Equation, operators: Operators) -> bool:
    evaluate = lambda total, op_num: op_num[0]((total, op_num[1]))
    test_result = functools.reduce(evaluate, zip(operators, equation.nums), 0)
    return test_result == equation.total


def test_equations(equations: Iterable[Equation], operators: Operators) -> int:
    calibration_result = 0
    for equation in equations:
        combinations = operator_combinations(operators, len(equation.nums))
        if any(
            test_equation(equation, operators) for operators in combinations
        ):
            calibration_result += equation.total

    return calibration_result


def concatenate(numbers: Iterable[int]) -> int:
    return int(''.join(str(num) for num in numbers))


if __name__ == '__main__':
    equations = parse_equations()

    print('Day 7, Part 1')
    with timer():
        result = test_equations(equations, (sum, math.prod))
    print(f'Result: {result}\n')    # 6083020304036

    print('Day 7, Part 2')
    with timer():
        result = test_equations(equations, (sum, math.prod, concatenate))
    print(f'Result: {result}\n')    # 59002246504791
