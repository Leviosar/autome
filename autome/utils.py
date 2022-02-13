from enum import Enum
from itertools import chain, combinations

class Direction(Enum):
    STAY = 0
    LEFT = 1
    RIGHT = 2
    S = 0
    L = 1
    R = 2


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return set(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))