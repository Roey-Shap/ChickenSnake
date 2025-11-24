def flatten(xss):
    return [x for xs in xss for x in xs]

def strings_have_overlap(s1, s2):
    return len(set(s1).intersection(set(s2))) > 0

def add_tuples(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return (t1[0] + t2[0], t1[1] + t2[1])

def sub_tuples(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return (t1[0] - t2[0], t1[1] - t2[1])

def multiply_tuples(t1: tuple[float, float], t2: tuple[float, float], do_round: bool=False) -> tuple[float, float]:
    x = t1[0] * t2[0]
    y = t1[1] * t2[1]
    return (round(x), round(y)) if do_round else (x, y)

def scale_tuple(t: tuple[float, float], s: float, do_round: bool=False) -> tuple[float, float] | tuple[int, int]:
    x = t[0] * s
    y = t[1] * s
    return (round(x), round(y)) if do_round else (x, y)

CARD_PIXEL_DIMS = (500, 700)
def scale_to_card_dims(percent_x, percent_y) -> tuple[float, float]:
    return (round(percent_x * CARD_PIXEL_DIMS[0]), round(percent_y * CARD_PIXEL_DIMS[1]))