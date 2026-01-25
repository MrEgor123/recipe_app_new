import math


def clamp_size(size: int) -> int:
    if size < 1:
        return 1
    if size > 50:
        return 50
    return size

def calc_offset(page: int, size: int) -> int:
    if page < 1:
        page = 1
    size = clamp_size(size)
    return (page - 1) * size

def calc_pages(total: int, size: int) -> int:
    size = clamp_size(size)
    if total <= 0:
        return 0
    return math.ceil(total / size)
