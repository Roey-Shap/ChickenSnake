def flatten(xss):
    return [x for xs in xss for x in xs]

def strings_have_overlap(s1, s2):
    return len(set(s1).intersection(set(s2))) > 0

def add_tuples(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return (t1[0] + t2[0], t1[1] + t2[1])

def multiply_tuples(t1: tuple[float, float], t2: tuple[float, float]) -> tuple[float, float]:
    return (t1[0] * t2[0], t1[1] * t2[1])