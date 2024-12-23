from __future__ import annotations

from collections import defaultdict
from typing import NewType, Tuple

from lib import read_input, timer


Network = NewType('Network', dict[str, set[str]])


def parse_input() -> Network:
    network = Network(defaultdict(set))
    pairs = (line.split('-') for line in read_input(23))
    for pair in pairs:
        tail, head = pair
        network[tail].add(head)
        network[head].add(tail)

    return network


def find_triples(network: Network) -> set[frozenset[str]]:
    triples = set()

    for node, neighbors in network.items():
        for neighbor in neighbors:
            shared_neighbors = neighbors & network[neighbor]
            for shared in shared_neighbors:
                triples.add(frozenset([node, neighbor, shared]))

    return triples


def find_groups(network: Network) -> set[frozenset[str]]:
    """
    Generalize part 1 with DFS through the network graph.

    Keep track of the path. The current node must be
    connected to all of the previous nodes for it to
    still be part of an interconnected group.

    Only continue to traverse paths for interconnected nodes.
    """
    groups = set()
    visited: set[Tuple[frozenset[str], str]] = set()

    def find_group(prev: set[str], node: str) -> None:
        visit = (frozenset(prev), node)
        if visit in visited:
            return
        visited.add(visit)

        neighbors = network[node]
        if prev.issubset(neighbors):
            new_group = prev | {node}
            groups.add(frozenset(new_group))
            for neighbor in neighbors - prev:
                find_group(new_group, neighbor)

    for node in network:
        find_group(set(), node)

    return groups


def maybe_has_chief(group: frozenset[str]) -> bool:
    return any(member for member in group if member.startswith('t'))


def narrow_chief_groups(network: Network) -> int:
    triples = find_triples(network)
    return sum(1 for triple in triples if maybe_has_chief(triple))


def biggest_group(groups: set[frozenset[str]]) -> str:
    biggest_group: frozenset[str] = frozenset([])
    for group in groups:
        if len(group) > len(biggest_group):
            biggest_group = group
    return ','.join(sorted(biggest_group))


if __name__ == '__main__':
    network = parse_input()

    print('Day 23, Part 1')
    with timer():
        result = narrow_chief_groups(network)
    print(f'Result: {result}\n')    # 1194

    print('Day 23, Part 2')
    with timer():
        groups = find_groups(network)
        biggest = biggest_group(groups)
    print(f'Result: {biggest}\n')    # bd,bu,dv,gl,qc,rn,so,tm,wf,yl,ys,ze,zr
