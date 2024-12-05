import copy

from collections import defaultdict
from typing import Iterable, NamedTuple, NewType

from lib import read_input, timer


class Rule(NamedTuple):
    l: int
    r: int


Update = NewType('Update', list[int])


class Printer:
    def __init__(self, rules: list[Rule], updates: list[Update]):
        self.updates = updates

        self.numbers_after = defaultdict(set)
        self.numbers_before = defaultdict(set)
        for rule in rules:
            self.numbers_after[rule.l].add(rule.r)
            self.numbers_before[rule.r].add(rule.l)

    @staticmethod
    def from_input(input: Iterable[str]):
        rules = []
        for line in input:
            if line == '':
                break
            l, r = line.split('|')
            rules.append(Rule(int(l), int(r)))

        updates = []
        for line in input:
            updates.append(Update([int(s) for s in line.split(',')]))

        return Printer(rules, updates)

    def validate_update(self, update) -> bool:
        for i, n in enumerate(update):
            before_n = set(update[:i])
            after_n = set(update[i + 1 :])
            if (
                self.numbers_after[n] & before_n
                or self.numbers_before[n] & after_n
            ):
                return False

        return True

    def validate_updates(self) -> Iterable[Update]:
        return (
            update for update in self.updates if self.validate_update(update)
        )

    def score_valid_updates(self) -> int:
        return sum(
            update[len(update) // 2] for update in self.validate_updates()
        )

    def repair_update(self, broken_update: Update) -> Update:
        update = copy.copy(broken_update)
        while not self.validate_update(update):
            for i, n in enumerate(update):
                misplaced_before = self.numbers_after[n] & set(update[:i])
                misplaced_after = self.numbers_before[n] & set(update[i + 1 :])

                if misplaced_before:
                    misplaced_index = update.index(misplaced_before.pop())
                    update.insert(i + 1, update.pop(misplaced_index))
                    break

                elif misplaced_after:
                    misplaced_index = update.index(misplaced_after.pop())
                    update.insert(i, update.pop(misplaced_index))
                    break

        return update

    def repair_updates(self) -> Iterable[Update]:
        return (
            self.repair_update(update)
            for update in self.updates
            if not self.validate_update(update)
        )

    def score_repaired_updates(self) -> int:
        return sum(
            update[len(update) // 2] for update in self.repair_updates()
        )


if __name__ == '__main__':
    printer = Printer.from_input(read_input(5))

    print('Day 5, Part 1')
    with timer():
        result = printer.score_valid_updates()
    print(f'Result: {result}\n')    # 6384

    print('Day 5, Part 2')
    with timer():
        result = printer.score_repaired_updates()
    print(f'Result: {result}\n')    # 5353
