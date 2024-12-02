from lib import read_input, timer


def parse_reports() -> list[list[int]]:
    reports = []
    for line in read_input(2):
        report = [int(n) for n in line.split(' ')]
        reports.append(report)
    return reports


def report_intervals(report: list[int]) -> list[int]:
    return [n - report[i - 1] for i, n in enumerate(report) if i > 0]


def is_safe(intervals: list[int], min_step: int, max_step: int):
    safely_increases = all(
        min_step <= step and step <= max_step for step in intervals
    )
    safely_decreases = all(
        -max_step <= step and step <= -min_step for step in intervals
    )
    return safely_increases or safely_decreases


def count_safe_reports(reports: list[list[int]], min_step: int, max_step: int) -> int:
    return sum(
        is_safe(report_intervals(report), min_step, max_step)
        for report in reports
    )


def count_safe_reports_dampened(reports: list[list[int]], min_step: int, max_step: int) -> int:
    safe_count = 0
    for report in reports:
        report_variations = (
            report[0:i] + report[i + 1 : len(report)]
            for i in range(len(report))
        )
        if any(
            is_safe(report_intervals(variation), min_step, max_step)
            for variation in report_variations
        ):
            safe_count += 1

    return safe_count


if __name__ == '__main__':
    reports = parse_reports()

    print('Day 2, Part 1')
    with timer():
        result = count_safe_reports(reports, min_step=1, max_step=3)
    print(f'Safe reports: {result}\n')  # 314

    print('Day 2, Part 2')
    with timer():
        result = count_safe_reports_dampened(reports, min_step=1, max_step=3)
    print(f'Safe reports: {result}\n')  # 373
