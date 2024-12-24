from __future__ import annotations
import itertools
import re

from collections import deque
from dataclasses import dataclass
from typing import Callable, NewType, Optional, Tuple

from lib import read_input, timer


Wires = NewType('Wires', dict[str, Optional[bool]])

Op = Callable[[bool, bool], bool]


@dataclass
class Gate:
    lhs: str
    op: Op
    rhs: str
    dst: str


class Gates:
    def __init__(self, wires: Wires, gates: list[Gate]):
        self._wires = wires
        self._x_width = len([w for w in self._wires if w.startswith('x')])
        self._y_width = len([w for w in self._wires if w.startswith('y')])
        self._z_width = len([w for w in self._wires if w.startswith('z')])

        self._gates = gates
        self._with_input: dict[str, list[Gate]] = {}
        self._with_output: dict[str, Gate] = {}
        for gate in self._gates:
            self._with_input.setdefault(gate.lhs, []).append(gate)
            self._with_input.setdefault(gate.rhs, []).append(gate)
            self._with_output[gate.dst] = gate

    def swap_dst(self, dst1: str, dst2: str) -> None:
        gate1 = self._with_output[dst1]
        gate2 = self._with_output[dst2]

        self._with_output.pop(gate1.dst)
        self._with_output.pop(gate2.dst)

        gate1.dst, gate2.dst = gate2.dst, gate1.dst

        self._with_output[gate1.dst] = gate1
        self._with_output[gate2.dst] = gate2

    @property
    def in_width(self) -> int:
        return self._x_width

    @property
    def out_width(self) -> int:
        return self._z_width

    def simulate(self) -> None:
        next = deque(self._gates)
        while next:
            gate = next.popleft()
            lhs_val = self._wires[gate.lhs]
            rhs_val = self._wires[gate.rhs]
            dst_val = self._wires[gate.dst]

            if lhs_val is None or rhs_val is None:
                continue

            if dst_val is not None:
                continue

            self._wires[gate.dst] = gate.op(lhs_val, rhs_val)
            next.extend(self._with_input.get(gate.dst, []))

    def read_z(self) -> Optional[int]:
        z_wires = sorted(
            [w for w in self._wires if w.startswith('z')], reverse=True
        )

        z_vals = []
        for z in z_wires:
            z_val = self._wires[z]
            if z_val is None:
                return None
            z_vals.append(str(int(z_val)))

        return int(''.join(z_vals), 2)

    def outputs(self, out: str) -> set[str]:
        """
        Returns all dst wires connected to out, including out. Used to
        identify potential gates with swapped outputs.
        """
        parents = set([out])

        next = deque([out])
        while next:
            dst = next.popleft()
            gate = self._with_output.get(dst)
            if not gate:
                continue

            inputs = [gate.lhs, gate.rhs]
            parents.update([x for x in inputs if x in self._with_output])

            next.extend(inputs)

        return parents

    def test(self, x: int, y: int) -> Tuple[bool, Optional[int]]:
        """
        Resets the input wires with the provided values of x and y,
        then simulates the result and checks addition correctness.
        """
        x_binary = format(x, f'0{self._x_width}b')
        y_binary = format(y, f'0{self._y_width}b')

        for w in self._wires:
            if w.startswith('x'):
                idx = int(w[1:])
                self._wires[w] = bool(int(x_binary[-(idx + 1)]))

            elif w.startswith('y'):
                idx = int(w[1:])
                self._wires[w] = bool(int(y_binary[-(idx + 1)]))

            else:
                self._wires[w] = None

        self.simulate()

        z = self.read_z()
        if z is None:
            passed = False
        elif z == x + y:
            passed = True
        else:
            passed = False
            # print(f'     LHS:  {x_binary}')
            # print(f'     RHS:  {y_binary}')
            # print(f'Expected: {expected_binary}')
            # print(f'Received: {format(z, f"0{self._z_width}b")}')

        return (passed, z)


def parse_input() -> Gates:
    input = read_input(24)

    wires = Wires({})
    for raw_wire in input:
        if raw_wire == '':
            break
        name, raw_value = raw_wire.split(': ')
        wires[name] = bool(int(raw_value))

    gate_list = []
    PATTERN = r'(?P<lhs>\w+) (?P<op>AND|OR|XOR) (?P<rhs>\w+) -> (?P<dst>\w+)'
    for raw_gate in input:
        m = re.match(PATTERN, raw_gate)
        assert m

        gate_wires = m.group('lhs', 'rhs', 'dst')
        for wire in gate_wires:
            wires.setdefault(wire, None)

        lhs, rhs, dst = gate_wires

        raw_op = m.group('op')
        op: Optional[Op] = None
        if raw_op == 'AND':
            op = lambda l, r: l and r
        elif raw_op == 'OR':
            op = lambda l, r: l or r
        elif raw_op == 'XOR':
            op = lambda l, r: l ^ r
        assert op

        gate_list.append(Gate(lhs, op, rhs, dst))
    gates = Gates(wires, gate_list)

    return gates


def failed_z_bits(
    expected_z: int, actual_z: Optional[int], width: int
) -> list[str]:
    out: list[str] = []
    if actual_z is None:
        return out

    expected_binary = format(expected_z, f'0{width}b')
    actual_binary = format(actual_z, f'0{width}b')
    for i in range(width):
        if expected_binary[i] != actual_binary[i]:
            z_idx = width - i - 1
            out.append(f'z{format(z_idx, "02d")}')
    return out


def test_suite(
    gates: Gates,
    collect: Optional[Callable[[int, int, Optional[int]], None]] = None,
) -> bool:
    width = gates.in_width
    zero = '0' * width
    for i in reversed(range(width)):
        with_one = zero[:i] + '1' + zero[i + 1 :]
        wire_id = width - i - 1

        for bx, by in itertools.combinations_with_replacement(
            [zero, with_one], 2
        ):
            x = int(bx, 2)
            y = int(by, 2)
            passed, z = gates.test(x, y)
            if not passed:
                if collect:
                    collect(x, y, z)
                else:
                    return False

    # Only run the full suite when narrowing the final combinations of swaps.
    # It otherwise adds too much runtime to data collection and swaps to try.
    if collect:
        return False

    one = '1' * width
    for i in reversed(range(width)):
        with_zero = one[:i] + '0' + one[i + 1 :]
        wire_id = width - i - 1

        for bx, by in itertools.combinations_with_replacement(
            [one, with_zero], 2
        ):
            x = int(bx, 2)
            y = int(by, 2)
            passed, z = gates.test(x, y)
            if not passed:
                if collect:
                    collect(x, y, z)
                else:
                    return False

    return True


if __name__ == '__main__':
    print('Day 24, Part 1')
    with timer():
        gates = parse_input()
        gates.simulate()
        result = gates.read_z()
    print(f'Result: {result}\n')    # 53190357879014

    print('Day 24, Part 2')
    """
    We need to find the 4 output wire swaps that will fix the adder.

    Create a test suite. Start with a simple test over each bit. 0+0, 0+1, 1+0, 1+1

    Identify which tests fail and which output bits are mismatched for the failing tests.

    For the mismatched bits, identify all output wires leading to those bits. These might be
    possible candidates for swapping wires. Try all pair combinations to see if any of them
    fix the test. If so, save that pair as a possible swap.

    After collecting all possible swaps from the test suite, try all combinations of 4 swaps
    to see which combination will fix the entire test suite.
    """
    with timer():
        possible_swaps: set[Tuple[str, str]] = set()

        def handle_test_failure(
            x: int, y: int, actual_z: Optional[int]
        ) -> None:
            mismatched_bits = failed_z_bits(x + y, actual_z, gates.out_width)
            possible_wires = set(
                all_outs
                for dst in mismatched_bits
                for all_outs in gates.outputs(dst)
            )

            for dst1, dst2 in itertools.combinations(possible_wires, 2):
                gates.swap_dst(dst1, dst2)

                passed, _ = gates.test(x, y)
                if passed:
                    possible_swaps.add(
                        (dst1, dst2) if dst1 < dst2 else (dst2, dst1)
                    )

                gates.swap_dst(dst1, dst2)

        test_suite(gates, handle_test_failure)

        print(f'{len(possible_swaps)} possible swaps that can fix the tests')

        """
        Across all the bit tests, there are 34 possible swaps that can fix the tests. I can
        try all valid combinations of 4 swaps, run the full test suites for each combo, and see
        which pass.
        """

        possible_combos = set()
        for combo in itertools.combinations(possible_swaps, 4):
            dsts = set(dst for swap in combo for dst in swap)

            if len(dsts) < 8:
                continue

            for swap in combo:
                gates.swap_dst(swap[0], swap[1])

            passed = test_suite(gates)
            if passed:
                possible_combos.add(combo)

            for swap in combo:
                gates.swap_dst(swap[0], swap[1])

        possible_solutions = [
            ','.join(sorted(dst for swap in combo for dst in swap))
            for combo in possible_combos
        ]
    print(
        f'Result: {possible_solutions}\n'
    )    # bks,hnd,nrn,tdv,tjp,z09,z16,z23
