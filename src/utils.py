from tqdm import tqdm
from math import gcd
from functools import reduce
from itertools import product, permutations


def encodeTuple(xs: tuple[int, ...], k: int):
    '''Кодирует кортеж из n чисел от 0 до k-1 в число.'''
    value = 0
    for x in xs:
        value = value * k + x
    return value

def decodeTuple(num: int, n: int, k: int) -> tuple[int, ...]:
    '''Возвращает кортеж из n чисел от 0 до k-1, кодируемый данным индексом.'''
    assert isinstance(num, int), num
    coord = []
    for _ in range(n):
        num, rem = divmod(num, k)
        coord.append(rem)
    res = tuple(reversed(coord))
    return res

def nextTuple(xs: tuple[int, ...] | list[int], k: int):
    '''Возвращает следующий кортеж ...'''
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
    '''
    Предикат, определяющий является ли perm перестановкой простого порядка.
    '''
    assert None not in perm
    if not isPermutation(perm):
        return False
    order = permutationOrder(perm)
    return isPrime(order)

def getNewSingletonElement(knownElems: set[int], allElems: set[int]):
    '''
    Возвращает синглтон от элемента, который ещё не знаком.
    Если такого нет, то возращает пустое множество.
    '''
    if len(allElems) != len(knownElems):
        return {min(allElems - knownElems)}
    else:
        return set[int]()
