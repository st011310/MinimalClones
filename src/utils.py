from numpy.typing import NDArray

from math import gcd
from functools import lru_cache
from itertools import product, permutations
import numpy as np


from tqdm import tqdm

from .utils_numba import decodeTuple_numba, encodeTuple_numba, isPrime_numba, permutationOrder_numba, compose_numba

def encodeTuple(xs: np.ndarray | tuple[int, ...], k: int):
    '''Кодирует кортеж из n чисел от 0 до k-1 в число.'''
    coord = np.asarray(xs, dtype=np.int32)
    return encodeTuple_numba(coord, k)

@lru_cache(maxsize=1024)
def decodeTuple(code: int, n: int, k: int) -> NDArray[np.int32]:
    '''Возвращает кортеж из n чисел от 0 до k-1, кодируемый данным индексом.'''
    assert isinstance(code, int), code
    out = np.empty(n, dtype=np.int32)
    decodeTuple_numba(code, n, k, out)
    return out

def nextTuple(xs: tuple[int, ...] | list[int], k: int):
    '''Возвращает следующий кортеж в порядке увеличения максимального элемента'''
    n = len(xs)
    assert n > 0, xs
    if n == 1:
        assert xs[0] < k
        return (xs[0] + 1,)

    if all(it == xs[0] for it in xs):
        assert xs[0] + 1 <= k, (xs[0], k)
        return tuple((n-1) *[0] + [xs[0] + 1])

    max_val = max(xs)
    if k > max_val:
        return nextTuple(xs, max_val)

    idx = xs.index(k)
    left = xs[:idx]
    if idx + 1 == n:
        if min(left) == k - 1:
            return (0,) * (n-2) + (k, 0)
        leftAns = nextTuple(left, k-1)
        return leftAns + (k,)
    right = xs[idx + 1:]
    if min(right) == k:
        if min(left) == k - 1:
           return tuple([0] * (len(left) - 1) + [k] + [0] * (len(right) + 1))
        leftAns = nextTuple(left, k-1)
        return leftAns + (k,) + right

    return tuple(left) + (k,) + nextTuple(right, k)

def tupleIterator(k: int, n: int):
    assert n >= 0, n
    assert k >= 1, k
    if n == 0:
        yield tuple()
        return
    if n == 1:
        for i in range(k):
            yield (i,)
        return
    if k == 1:
        yield (0,) * n
        return

    for i in tupleIterator(k-1, n):
        yield i
    for i in reversed(range(n)):
        for left in tupleIterator(k-1, i):
            for right in tupleIterator(k, n-i-1):
                yield left + (k-1,) + right

def reval(table: list):
    if not isinstance(table[0], int) and table[0] is not None:
        table = sum([reval(subtable) for subtable in table], start=[])
    return table

def make_nested(size: int, depth: int):
    """Создаёт depth-мерный список размера size, заполненный None."""
    if depth == 1:
        return [None] * size
    return [make_nested(size, depth - 1) for _ in range(size)]


def conjugateTable(table: list[int], n: int, k: int, psi: tuple):
    """
    table: список длины k^n.
    table[index(x1,...,xn)] = f(x1,...,xn)
    psi: перестановка значений 0..k-1
    """
    assert isinstance(table, (tuple, list))
    assert len(table) > 0
    assert isinstance(table[0], int)

    psi_inv = [0] * k
    for i, p in enumerate(psi):
        psi_inv[p] = i

    new_table = [0] * (k ** n)

    for x in product(range(k), repeat=n):
        px = tuple(psi[a] for a in x)

        old_index = encodeTuple(px, k)
        value = table[old_index]

        # psi^{-1}(f(psi(x)))
        new_value = psi_inv[value]

        new_index = encodeTuple(x, k)
        new_table[new_index] = new_value

    return tuple(new_table)


def canonicalTable(table: list, n: int, k: int):
    best = None

    for psi in permutations(range(k)):
        t = conjugateTable(reval(table), n, k, psi)
        if best is None or t < best:
            best = t
    return best

def removeConjugates(functions: list[list], n: int, k: int):
    """
    functions: список таблиц истинности.
    Возвращает список представителей классов сопряжённости.
    """
    seen = {}
    result = list[list]()

    for table in tqdm(functions):
        key = canonicalTable(table, n, k)
        if key not in seen:
            seen[key] = table
            result.append(table)
        else:
            t1 = seen[key]
            if table < t1:
                seen[key] = table
                result.remove(t1)
                result.append(table)
    return result

def lcm(a, b):
    '''НОК'''
    return a * b // gcd(a, b)

def isPermutation(perm: list):
    assert None not in perm
    n_numbers = len(perm)
    unique_nums = len(set(perm))
    return n_numbers == unique_nums

def isPrimePermutation(perm: list) -> bool:
    '''
    Предикат, определяющий является ли perm перестановкой простого порядка.
    '''
    assert None not in perm
    if not isPermutation(perm):
        return False
    order = permutationOrder_numba(np.array(perm))
    return isPrime_numba(order)

def getNewSingletonElement(knownElems: set[int], allElems: set[int]):
    '''
    Возвращает синглтон от элемента, который ещё не знаком.
    Если такого нет, то возращает пустое множество.
    '''
    if len(allElems) != len(knownElems):
        return {min(allElems - knownElems)}
    else:
        return set[int]()


def _list_to_array(lst: list, dtype=np.int32) -> np.ndarray:
    arr = np.empty(len(lst), dtype=dtype)
    for i, v in enumerate(lst):
        arr[i] = -1 if v is None else v
    return arr

def _array_to_list(arr: np.ndarray) -> list:
    return [None if v == -1 else int(v) for v in arr]

def compose(f_body: list[int | None], gi_body: list[list[int | None] | None], N: int, K: int) -> list[int | None]:
    size = len(f_body)
    g_data = np.empty((N, size), dtype=np.int32)
    g_is_proj = np.empty(N, dtype=np.bool_)

    for i, g in enumerate(gi_body):
        if g is None:
            g_is_proj[i] = True
            # g_data[i, :] = 0
        else:
            g_is_proj[i] = False
            g_data[i, :] = _list_to_array(g)

    f_arr = _list_to_array(f_body)
    h_arr = compose_numba(f_arr, g_data, g_is_proj, N, K)
    return _array_to_list(h_arr)