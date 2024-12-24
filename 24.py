from __future__ import annotations
import re

from collections import deque
from typing import Callable, NamedTuple, NewType, Optional

from lib import read_input, timer


Wires = NewType('Wires', dict[str, Optional[bool]])

Op = Callable[[bool, bool], bool]


class Gate(NamedTuple):
    lhs: str
    op: Op
    rhs: str
    dst: str


class Gates:
    def __init__(self, wires: Wires, gates: list[Gate]):
        self._wires = wires
        self._gates = gates
        self._with_input: dict[str, list[Gate]] = {}
        for gate in self._gates:
            self._with_input.setdefault(gate.lhs, []).append(gate)
            self._with_input.setdefault(gate.rhs, []).append(gate)

    def simulate(self) -> None:
        next = deque(self._gates)
        while next:
            gate = next.popleft()
            lhs_val = self._wires[gate.lhs]
            rhs_val = self._wires[gate.rhs]
            dst_val = self._wires[gate.dst]

            if lhs_val is None or rhs_val is None:
                next.append(gate)
                continue

            if dst_val is not None:
                continue

            self._wires[gate.dst] = gate.op(lhs_val, rhs_val)
            next.extend(self._with_input.get(gate.dst, []))

    def read_z(self) -> int:
        z_wires = sorted(
            [w for w in self._wires if w.startswith('z')], reverse=True
        )

        z_vals = []
        for z in z_wires:
            z_val = self._wires[z]
            assert z_val is not None
            z_vals.append(str(int(z_val)))

        return int(''.join(z_vals), 2)


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


if __name__ == '__main__':
    print('Day 24, Part 1')
    with timer():
        gates = parse_input()
        gates.simulate()
        result = gates.read_z()
    print(f'Result: {result}\n')    # 53190357879014

    print('Day 24, Part 2')
    with timer():
        result = 0
    print(f'Result: {result}\n')    #
