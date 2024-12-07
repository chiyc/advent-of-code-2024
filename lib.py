import os


from time import perf_counter
from types import TracebackType
from typing import Iterable, Union

from urllib import request


def read_input(day: Union[int, str]) -> Iterable[str]:
    url = f'https://adventofcode.com/2024/day/{day}/input'
    session = os.environ.get('AOC_SESSION')
    req = request.Request(url, headers={'Cookie': f'session={session}'})
    with request.urlopen(req) as f:
        for _line in f.readlines():
            yield _line.decode('utf-8').strip()


class timer:
    """
    https://stackoverflow.com/questions/33987060/python-context-manager-that-measures-time
    """

    def __enter__(self) -> timer:
        self.start = perf_counter()
        return self

    def __exit__(
        self,
        _type: type[BaseException],
        _value: BaseException,
        _traceback: TracebackType,
    ) -> None:
        self.time = perf_counter() - self.start
        print(f'Elapsed (ms): {self.time*1000:.3f}')
