import re

from dataclasses import dataclass, field
from typing import NewType

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


def run_computer(cpu: Computer) -> None:
    reg = cpu.registers
    while cpu.ip < len(cpu.program):
        step = 2

        instr = cpu.program[cpu.ip]
        operand = cpu.program[cpu.ip + 1]

        if instr == 0:
            reg.a = reg.a // 2 ** combo(operand, reg)
        elif instr == 1:
            reg.b = reg.b ^ operand
        elif instr == 2:
            reg.b = combo(operand, reg) % 8
        elif instr == 3:
            if reg.a != 0:
                cpu.ip = operand
                step = 0
        elif instr == 4:
            reg.b = reg.b ^ reg.c
        elif instr == 5:
            cpu.output.append(combo(operand, reg) % 8)
        elif instr == 6:
            reg.b = reg.a // 2 ** combo(operand, reg)
        elif instr == 7:
            reg.c = reg.a // 2 ** combo(operand, reg)
        else:
            assert False

        cpu.ip += step


if __name__ == '__main__':
    run_tests()

    computer = parse_input()

    print('Day 17, Part 1')
    with timer():
        run_computer(computer)
        result = ','.join(str(n) for n in computer.output)
    print(f'Result: {result}\n')    # 1,5,3,0,2,5,2,5,3

    print('Day 17, Part 2')
    with timer():
        result = ''
    print(f'Result: {result}\n')    #
