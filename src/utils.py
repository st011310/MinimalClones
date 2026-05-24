from math import gcd
from functools import reduce
from itertools import product, permutations
from typing import Iterable

def encodeTuple(xs: tuple[int, ...], k: int):
    '''Кодирует кортеж из n чисел от 0 до k-1 в число.'''
    value = 0
    for x in xs:
        value = value * k + x
    return value


def decodeTuple(index: int, n: int, k: int) -> tuple[int, ...]:
    '''Возвращает кортеж из n чисел от 0 до k-1, кодируемый данным индексом.'''
    xs = []
    for _ in range(n):
        xs.append(index % k)
        index //= k
    return tuple(reversed(xs))

def nextTuple(xs: tuple[int, ...], k: int):
    '''Возвращает следующий кортеж в лексикографическом порядке.'''
    n = len(xs)
    return decodeTuple((encodeTuple(xs, k) + 1) % (k ** n), n, k)

def prevTuple(xs: tuple[int, ...], k: int):
    '''Возвращает предыдущий кортеж в лексикографическом порядке.'''
    n = len(xs)
    return decodeTuple((encodeTuple(xs, k) - 1) % (k ** n), n, k)

def conjugateTable(table, n: int, k: int, psi: tuple):
    """
    table: список длины k^n.
    table[index(x1,...,xn)] = f(x1,...,xn)
    psi: перестановка значений 0..k-1
    """
    assert isinstance(table, (tuple, list))
    assert len(table) > 0
    if isinstance(table[0], (tuple, list)):
        table = [x for row in table for x in row]
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


def canonicalTable(table, n: int, k: int):
    best = None
    print("Canonicalizing", table)

    for psi in permutations(range(k)):
        t = conjugateTable(table, n, k, psi)
        if best is None or t < best:
            best = t
            print("New best:", best, "with psi =", psi)
    # print("Canonical form:", best)
    return best


def removeConjugates(functions, n: int, k: int):
    """
    functions: список таблиц истинности.
    Возвращает список представителей классов сопряжённости.
    """
    seen = {}
    result = []

    for table in functions:
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
    return a * b // gcd(a, b)

def isPermutation(perm: list):
    assert None not in perm
    n_numbers = len(perm)
    unique_nums = len(set(perm))
    return n_numbers == unique_nums

def isPrime(n: int):
    """Проверка, является ли число простым."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def permutationOrder(perm):
    """
    perm: список, представляющий перестановку в виде [p(0), p(1), ..., p(n-1)]
    Возвращает порядок перестановки.
    """
    n = len(perm)
    visited = [False] * n
    cycle_lengths = []
    for i in range(n):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                length += 1
            if length > 0:
                cycle_lengths.append(length)
    if not cycle_lengths:
        return 1
    return reduce(lcm, cycle_lengths)

def isPrimePermutation(perm: list):
    assert None not in perm
    if not isPermutation(perm):
        return False
    order = permutationOrder(perm)
    return isPrime(order)

def getNewSingletonElement(knownElems: set[int], allElems: set[int]):
    if len(allElems) != len(knownElems):
        return {min(allElems - knownElems)}
    else:
        return set()
