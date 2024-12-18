import re

from dataclasses import dataclass, field
from typing import Optional

from lib import read_input, timer


@dataclass
class Registers:
    a: int
    b: int
    c: int


@dataclass
class Computer:
    registers: Registers
    program: list[int]
    output: list[int] = field(default_factory=list)
    ip: int = 0


PATTERN = r'Register A: (?P<A>\d+)\nRegister B: (?P<B>\d+)\nRegister C: (?P<C>\d+)\n\nProgram: (?P<Program>[\d,]+)'


def parse_input() -> Computer:
    input = '\n'.join(line for line in read_input(17))

    m = re.match(PATTERN, input, re.MULTILINE)
    assert m
    a, b, c, program = m.group('A', 'B', 'C', 'Program')

    return Computer(
        Registers(int(a), int(b), int(c)),
        [int(n) for n in program.split(',')],
    )


def run_tests() -> None:
    cpu = Computer(Registers(0, 0, 9), [2, 6])
    run_computer(cpu)
    assert cpu.registers.b == 1

    cpu = Computer(Registers(10, 0, 0), [5, 0, 5, 1, 5, 4])
    run_computer(cpu)
    assert cpu.output == [0, 1, 2]

    cpu = Computer(Registers(2024, 0, 0), [0, 1, 5, 4, 3, 0])
    run_computer(cpu)
    assert cpu.output == [4, 2, 5, 6, 7, 7, 7, 7, 3, 1, 0]
    assert cpu.registers.a == 0

    cpu = Computer(Registers(0, 29, 0), [1, 7])
    run_computer(cpu)
    assert cpu.registers.b == 26

    cpu = Computer(Registers(0, 2024, 43690), [4, 0])
    run_computer(cpu)
    assert cpu.registers.b == 44354

    cpu = Computer(Registers(729, 0, 0), [0, 1, 5, 4, 3, 0])
    run_computer(cpu)
    assert cpu.output == [4, 6, 3, 5, 6, 3, 5, 2, 1, 0]


def combo(operand: int, registers: Registers) -> int:
    assert 0 <= operand <= 6
    if 0 <= operand <= 3:
        return operand
    elif operand == 4:
        return registers.a
    elif operand == 5:
        return registers.b
    elif operand == 6:
        return registers.c
    else:
        assert False


def run_computer(cpu: Computer, reg_a: Optional[int] = None) -> None:
    cpu.ip = 0
    cpu.output = []
    if reg_a is not None:
        cpu.registers = Registers(reg_a, 0, 0)

    reg = cpu.registers
    while cpu.ip < len(cpu.program):
        step = 2

        instr = cpu.program[cpu.ip]
        operand = cpu.program[cpu.ip + 1]

        if instr == 0:   # adv
            reg.a = reg.a // 2 ** combo(operand, reg)
        elif instr == 1:   # bxl
            reg.b = reg.b ^ operand
        elif instr == 2:   # bst
            reg.b = combo(operand, reg) % 8
        elif instr == 3:   # jnz
            if reg.a != 0:
                cpu.ip = operand
                step = 0
        elif instr == 4:   # bxc
            reg.b = reg.b ^ reg.c
        elif instr == 5:   # out
            cpu.output.append(combo(operand, reg) % 8)
        elif instr == 6:   # bdv
            reg.b = reg.a // 2 ** combo(operand, reg)
        elif instr == 7:   # cdv
            reg.c = reg.a // 2 ** combo(operand, reg)
        else:
            assert False

        cpu.ip += step


def do_part2(cpu: Computer) -> int:
    """
    My input program is [2,4, 1,3, 7,5, 4,1, 1,3, 0,3, 5,5, 3,0]

    opcode     2   1   7   4   1   0   5   3
    instr     bst bxl cdv bxc bxl adv out jnz
    operand    4   3   5   -   3   3   5   0
    c or l     c   l   c   -   l   c   c   l
    value      a   3   b   -   3   3   b   0
    store      b   b   c   b   b   a   -   -

    We can see that the program loops until reg.a hits 0. reg.a is divided by the same constant on
    each iteration.

    Using subscripts to easily see how register values depend on each other,

    b0 <= a % 8
    b1 <= b0 ^ 3
    c  <= a // 2 ** b1
    b2 <= b1 ^ c
    b3 <= b2 ^ 3

    a_next <= a // 2 ** 3
    output <= b3 % 8
    repeat if a_next != 0

    Note that reg.a //= 8 on each iteration until it hits 0, at which point the program ends.
    This means that in the last iteration, 1 <= reg.a <= 7. It would've halted already if it were 0,
    and if it were 8, then reg.a //= 8 == 1, and there would be another iteration.

    Each iteration also only depends on the value of reg.a at the start of the iteration.
    We can see that reg.b is written to based on the starting value of reg.a, and
    reg.c is then computed from reg.a and reg.b

    Testing all possible reg.a values for 16 length output would require 246,290,604,621,824 iterations

    We can instead work backwards from the final output item, test only the reduced set of possible
    values for reg.a, then in the next iteration, test the possible values reg.a would've been in
    the previous iteration. Continue until we get the final answer.
    """
    final_output = cpu.program.copy()

    # Start with these values of reg.a
    a_set = [1, 2, 3, 4, 5, 6, 7]
    # Process the final output in reverse
    for i in reversed(range(0, len(final_output))):
        output = final_output[i:]
        next_a = []
        for a in a_set:
            # Run the computer for each value of reg.a
            run_computer(cpu, a)

            # If this is the final iteration and matches the whole output,
            # we want the current value of a
            if cpu.output == output and i == 0:
                next_a.append(a)

            # Otherwise, collect the next set of values to test
            elif cpu.output == output:
                # Getting the range of next register A values to test here depends
                # on knowing that it goes through integer division by 8 each time.
                next_a.extend(range(a * 8, (a + 1) * 8))

        a_set = next_a

    return min(a_set)


if __name__ == '__main__':
    run_tests()

    print('Day 17, Part 1')
    computer = parse_input()
    with timer():
        run_computer(computer)
        result = ','.join(str(n) for n in computer.output)
    print(f'Result: {result}\n')    # 1,5,3,0,2,5,2,5,3

    print('Day 17, Part 2')
    computer = parse_input()
    with timer():
        result = str(do_part2(computer))
    print(f'Result: {result}\n')    # 108107566389757
