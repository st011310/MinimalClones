import numba
import numpy as np

@numba.njit
def encodeTuple_numba(arr: np.ndarray, k: int) -> int:
    value = 0
    for x in arr:
        value = value * k + x
    return value

@numba.njit
def decodeTuple_numba(num: int, n: int, k: int, out: np.ndarray):
    for i in range(n - 1, -1, -1):
        out[i] = num % k
        num //= k

@numba.njit
def gcd_numba(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

@numba.njit
def lcm_numba(a: int, b: int) -> int:
    return a // gcd_numba(a, b) * b

@numba.njit
def isPrime_numba(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

@numba.njit
def permutationOrder_numba(perm: np.ndarray) -> int:
    """
    perm: список, представляющий перестановку в виде [p(0), p(1), ..., p(n-1)]
    Возвращает порядок перестановки.
    """
    n = perm.shape[0]
    visited = np.zeros(n, dtype=np.bool_)
    order = 1
    for i in range(n):
        if not visited[i]:
            length = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
                length += 1
            if length:
                order = lcm_numba(order, length)
    return order


@numba.njit
def compose_numba(f_body: np.ndarray,       # 1D int32, -1 = None
                  g_data: np.ndarray,       # 2D int32, shape (N, size)
                  g_is_proj: np.ndarray,    # 1D bool, длина N
                  N: int, K: int) -> np.ndarray:
    size = f_body.shape[0]
    h_body = np.empty(size, dtype=np.int32)
    coord = np.empty(N, dtype=np.int32)
    args = np.empty(N, dtype=np.int32)

    for idx in range(size):
        # Восстанавливаем координаты
        tmp = idx
        for i in range(N - 1, -1, -1):
            coord[i] = tmp % K
            tmp //= K

        undefined = False
        for i in range(N):
            if g_is_proj[i]:
                args[i] = coord[i]
            else:
                g_idx = 0
                for j in range(N):
                    g_idx = g_idx * K + coord[j]
                val = g_data[i, g_idx]
                if val == -1:
                    undefined = True
                    break
                args[i] = val

        if undefined:
            h_body[idx] = -1
            continue

        # Индекс в f_body
        f_idx = 0
        for j in range(N):
            f_idx = f_idx * K + args[j]
        h_body[idx] = f_body[f_idx]   # если f_body[f_idx] == -1, то -1 останется

    return h_body