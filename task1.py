from pprint import pprint
from math import modf

A = {
    'asasa' : 12212,
    'ololo' : "azazaza",
    'gggg'  : 3.20301,
    'hlo'   : [
        1, 2, 3
    ],
    'fff' : {
        'a1' : 0,
        'a2' : "vv1112aas"
    }
}
B = {
    'asasa' : 12212,
    'ololo' : "azazaza",
    'gggg'  : 3.20301,
    'hlo'   : [
        1, 2, 3,
    ],
    'fff' : {
        'a1' : 0,
        'a2' : "vv1112aas"
    }
}


def compare_floats(a: float, b: float, precision: int = 5) -> bool:
    quantifier = 10 ** precision
    aint = int(modf(a)[1])
    bint = int(modf(b)[1])

    if aint != bint:
        return False

    afrac = int(modf(modf(a)[0] * quantifier)[1])
    bfrac = int(modf(modf(b)[0] * quantifier)[1])

    if afrac != bfrac:
        return False

    return True


def icompare(A, B, float_precision=5) -> bool:
    if type(A) != type(B):
        return False

    if A is None:
        return True

    # dict
    if type(A) == dict:
        Ak = A.keys()
        Bk = B.keys()

        # исключим заведомо отрицательный вариант
        if sorted(Ak) != sorted(Bk):
            return False

        for k in Ak:
            if not icompare(A[k], B[k]):
                return False

    if type(A) == list:
        # исключим заведомо отрицательный вариант
        if len(A) != len(B):
            return False
        for i in range(len(A)):
            if not icompare(A[i], B[i]):
                return False

    # str, int, float
    if (type(A) in [int, str] and A != B) or \
            (type(A) == float and not compare_floats(A, B, precision=float_precision)):
        return False

    return True

# ==========================
pprint(A)
pprint(B)

print( icompare(A, B) )

