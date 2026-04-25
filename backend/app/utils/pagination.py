import math


def calculate_pages(total: int, per_page: int) -> int:
    return max(1, math.ceil(total / per_page))
