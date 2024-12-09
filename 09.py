from __future__ import annotations
import array
import bisect
import copy

from collections import deque
from typing import NamedTuple, NewType

from lib import read_input, timer


class Block(NamedTuple):
    id: int
    loc: int
    size: int

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Block):
            raise NotImplemented
        return self.loc < other.loc


Disk = NewType('Disk', array.array[int])


class DiskMap(NamedTuple):
    disk: Disk
    files: list[Block]
    free: deque[Block]


def parse_dense_disk_map() -> list[int]:
    dense_disk_map = [int(n) for line in read_input(9) for n in str(line)]
    return dense_disk_map


def dense_disk_map_size(dense_disk_map: list[int]) -> int:
    return sum(dense_disk_map)


def read_dense_disk_map(dense_disk_map: list[int]) -> DiskMap:
    disk: Disk = Disk(array.array('h', []))
    files: list[Block] = []
    free_spaces: deque[Block] = deque()

    for i, size in enumerate(dense_disk_map):
        next_loc = len(disk)
        if i % 2 == 0:   # File
            file_id = i // 2
            files.append(Block(file_id, next_loc, size))
            disk.extend([file_id] * size)

        elif i % 2 == 1 and size:   # Free space
            free_spaces.append(Block(-1, next_loc, size))
            disk.extend([-1] * size)

    assert all(block.size > 0 for block in files)
    assert all(block.size > 0 for block in free_spaces)

    return DiskMap(disk, files, free_spaces)


def compact_disk_map(disk_map: DiskMap) -> DiskMap:
    while disk_map.free:
        last_file = disk_map.files[-1]
        file_size_left = last_file.size

        while file_size_left and disk_map.free:
            next_free = disk_map.free[0]
            free_start = next_free.loc
            free_end = min(
                free_start + file_size_left,
                free_start + next_free.size,
            )
            file_size_moved = free_end - free_start
            file_size_left -= file_size_moved
            free_size_left = next_free.size - file_size_moved

            disk_map.disk[free_start:free_end] = array.array(
                'h', [last_file.id] * file_size_moved
            )
            del disk_map.disk[last_file.loc + file_size_left :]

            if not free_size_left:
                disk_map.free.popleft()
            else:
                disk_map.free[0] = Block(-1, free_end, free_size_left)

            if not file_size_left:
                disk_map.files.pop()
                if (
                    disk_map.free
                    and disk_map.files[-1].loc < disk_map.free[-1].loc
                ):
                    disk_map.free.pop()
            else:
                disk_map.files[-1] = Block(
                    last_file.id, last_file.loc, file_size_left
                )

            new_file_block = Block(last_file.id, free_start, file_size_moved)
            disk_map.files.insert(
                bisect.bisect_right(disk_map.files, new_file_block),
                new_file_block,
            )

    return disk_map


def compact_disk_map_unfragmented(disk_map: DiskMap) -> DiskMap:
    compacted_files = copy.copy(disk_map.files)
    for file in reversed(disk_map.files):
        for i, free in enumerate(disk_map.free):
            if free.loc > file.loc:
                break

            if free.size >= file.size:
                free_start = free.loc
                free_end = free_start + file.size

                disk_map.disk[free_start:free_end] = array.array(
                    'h', [file.id] * file.size
                )
                disk_map.disk[file.loc : file.loc + file.size] = array.array(
                    'h', [-1] * file.size
                )

                old_file_block_index = bisect.bisect_left(compacted_files, file)
                del compacted_files[old_file_block_index]

                compacted_file_block = Block(file.id, free_start, file.size)
                compacted_files.insert(
                    bisect.bisect_right(compacted_files, compacted_file_block),
                    compacted_file_block,
                )

                free_size_left = free.size - file.size
                if not free_size_left:
                    del disk_map.free[i]
                else:
                    disk_map.free[i] = Block(
                        -1, free_start + file.size, free_size_left
                    )

                break

    return DiskMap(
        disk_map.disk,
        compacted_files,
        disk_map.free,
    )


def disk_checksum(disk: Disk) -> int:
    return sum(
        [idx * file_id for idx, file_id in enumerate(disk) if file_id >= 0]
    )


if __name__ == '__main__':
    dense_disk_map = parse_dense_disk_map()

    print('Day 9, Part 1')
    with timer():
        disk_map = read_dense_disk_map(dense_disk_map)
        compacted_disk_map = compact_disk_map(disk_map)
        result = disk_checksum(compacted_disk_map.disk)
    print(f'Result: {result}\n')    # 6421128769094

    print('Day 9, Part 2')
    with timer():
        disk_map = read_dense_disk_map(dense_disk_map)
        compacted_disk_map = compact_disk_map_unfragmented(disk_map)
        result = disk_checksum(compacted_disk_map.disk)
    print(f'Result: {result}\n')    # 6448168620520
