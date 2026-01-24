import math
from dataclasses import astuple, dataclass

def flatten(xss):
    return [x for xs in xss for x in xs]

def strings_have_overlap(s1, s2):
    return len(set(s1).intersection(set(s2))) > 0

class Tupe():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.min = x
        self.max = y

    def __add__(self, other):
        return Tupe(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Tupe(self.x - other.x, self.y - other.y)

    def scale(self, scalar, do_round=False):
        res: Tupe = Tupe(self.x * scalar, self.y * scalar)
        if do_round:
            return Tupe.round(res)
        else:
            return res
    
    def __mul__(self, other):
        return Tupe(self.x * other.x, self.y * other.y)

    def copy(self):
        return Tupe(self.x, self.y)

    @staticmethod
    def to_tuple(t) -> tuple:
        return (t.x, t.y)

    def __iter__(self):
        return iter((self.x, self.y))

    @staticmethod
    def round(t):
        return Tupe(round(t.x), round(t.y))

    def __repr__(self):
        return f"Tupe {self.x}, {self.y}"

def map_value(value, pre_range: Tupe, post_range: Tupe):
    d_prev: float = pre_range.max - pre_range.min
    d_post: float = post_range.max - post_range.min
    v = post_range.min + (value - pre_range.min) * (d_post / d_prev)
    print(v)
    return v

def rotate_vector(v: Tupe, radians: float):
    c, s = math.cos(radians), -math.sin(radians)
    # rotation_matrix = ((c, -s), (s, c)))
    def dot(t1: Tupe, t2: Tupe):
        return (t1.x * t2.x) + (t1.y * t2.y)

    return Tupe(dot(v, Tupe(c, -s)),
                dot(v, Tupe(s,  c))
                )

# def add_tuples(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
#     return (t1[0] + t2[0], t1[1] + t2[1])

# def sub_tuples(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
#     return (t1[0] - t2[0], t1[1] - t2[1])

# def multiply_tuples(t1: tuple[float, float], t2: tuple[float, float], do_round: bool=False) -> tuple[float, float]:
#     x = t1[0] * t2[0]
#     y = t1[1] * t2[1]
#     return (round(x), round(y)) if do_round else (x, y)

# def scale_tuple(t: tuple[float, float], s: float, do_round: bool=False) -> tuple[float, float] | tuple[int, int]:
#     x = t[0] * s
#     y = t[1] * s
#     return (round(x), round(y)) if do_round else (x, y)

CARD_PIXEL_DIMS = Tupe(500, 700)
def scale_to_card_dims(percent_x, percent_y) -> Tupe:
    return Tupe.round(Tupe(percent_x, percent_y) * CARD_PIXEL_DIMS)