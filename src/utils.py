from math import gcd
from functools import reduce
from collections import defaultdict

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


def canonicalFunction(f):
    """
    f: list/array длины N, f[i] = f(i)
    Возвращает хешируемый канонический представитель.
    """
    N = len(f)
    visited = [False] * N
    components = []

    for start in range(N):
        if visited[start]:
            continue
        path = []
        curr = start
        while not visited[curr]:
            visited[curr] = True
            path.append(curr)
            curr = f[curr]

        cycle_start = path.index(curr) if curr in path else -1
        cycle = path[cycle_start:] if cycle_start != -1 else []
        # trees_nodes = set(path[:cycle_start])

        rev_adj = defaultdict(list)
        for u in path[:cycle_start]:
            rev_adj[f[u]].append(u)

        def canon_tree(root):
            stack = [(root, False)]
            results = {}
            while stack:
                node, processed = stack.pop()
                if not processed:
                    stack.append((node, True))
                    for child in rev_adj[node]:
                        stack.append((child, False))
                else:
                    childs_canon = sorted(results[child] for child in rev_adj[node])
                    results[node] = "(" + "".join(childs_canon) + ")"
            return results[root]
        tree_canons = [canon_tree(node) for node in cycle]
        min_shift = min(range(len(tree_canons)),
                        key=lambda i: tuple(tree_canons[i:] + tree_canons[:i]))
        comp_canon = "".join(tree_canons[min_shift:] + tree_canons[:min_shift])
        components.append(comp_canon)

    return tuple(sorted(components))

def removeIsomorphicFunctions(func_list: list[int]):
    seen = {}
    result = []
    for f in func_list:
        canon = canonicalFunction(f)
        if canon not in seen:
            seen[canon] = f
            result.append(f)
    return result