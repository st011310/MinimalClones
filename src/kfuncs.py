from copy import deepcopy
from itertools import product, permutations
from libs.branch_bound import Entity
from .utils import isPrimePermutation, getNewSingletonElement, nextTuple, reval, make_nested, decodeTuple

class FuncN(Entity):
    def __init__(self, N: int, K: int) -> None:
        super().__init__()
        self.N = N
        self.K = K
        self.allElems = set(range(K))
        self.body = make_nested(K, N)
        self.nextCoord = (0,) * N
        self.knownElems = set[int]()
        self.deaph = 0

    def inplace_copy(self, of: 'FuncN'):
        self.body = deepcopy(of.body)
        self.nextCoord = nextTuple(of.nextCoord, of.K)
        self.deaph = of.deaph + 1
        self.knownElems = set()
        return self

    @classmethod
    def copy(cls, of: 'FuncN'):
        self = cls(of.N, of.K)
        self.inplace_copy(of)
        return self

    def branches(self):
        t = type(self)
        if self.N > 1 and all(x == self.nextCoord[0] for x in self.nextCoord):
            i = self.nextCoord[0]
            obj = t.copy(self)
            obj[self.nextCoord] = i
            obj.knownElems = self.knownElems | {i}
            yield obj
            return

        knownElems = self.knownElems | set(self.nextCoord)
        newElemSet = getNewSingletonElement(knownElems, self.allElems)
        for val in knownElems | newElemSet:
            obj = t.copy(self)
            obj[self.nextCoord] = val
            obj.knownElems = knownElems | {val}
            yield obj

    def isComplete(self) -> bool:
        return all(v is not None for v in reval(self.body))

    def isCorrect(self):
        '''Функция минимальна среди порождающих функций'''
        if self.N <= 1:
            return True
        for funcs in permutations([self] + [None] * (self.N - 1)):
            ans = self.compose(*funcs)
            if ans < self:
                return False
        return True

    def isSuitable(self) -> bool:
        """Проверяет идемпотентность на диагонали: f(i,i,...,i) == i для всех i."""
        for i in range(self.K):
            if self[(i,) * self.N] != i:
                return False
        return True

    def compose(self, *gs: 'FuncN') -> 'FuncN':
        """
        Возвращает новую функцию h(x) = f(g₁(x), …, gₙ(x)),
        где x = (x₁,…,xₙ).  Все gᵢ должны иметь ту же арность, что и f.
        """
        assert len(gs) == self.N
        assert all(g.N == self.N for g in gs if g is not None)

        h = FuncN(self.N, self.K)
        for coord in product(range(self.K), repeat=self.N):
            args = tuple(
                g[coord] if g is not None else coord[i]
                    for i, g in enumerate(gs)
            )
            h[coord] = self[args]
        return h

    def self_apply(self) -> 'FuncN':
        """
        Самоподстановка: f̃(x) = f( f(x), …, f(x) ).
        """
        return self.compose(*([self] * self.N))

    def pack(self) -> int:
        assert self.isComplete()
        ans = 0
        for dig in reval(self.body):
            ans = ans * self.K + dig
        return ans

    def unpack(self, code: int):
        for i in range(self.K ** self.N):
            coord = decodeTuple(self.K ** self.N - 1 - i, self.N, self.K)
            self[coord] = code % self.K
            code //= self.K
        return self

    def __getitem__(self, key):
        """key – кортеж длины N."""
        if not isinstance(key, tuple) or len(key) != self.N:
            raise KeyError(f"Требуется кортеж длины {self.N}")
        if any(idx is None for idx in key):
            return None

        val = self.body
        for idx in key:
            val = val[idx]
        assert isinstance(val, (int, type(None)))
        return val

    def __setitem__(self, key, value):
        if not isinstance(key, tuple) or len(key) != self.N:
            raise KeyError(f"Требуется кортеж длины {self.N}")
        *head, last = key
        arr = self.body
        for idx in head:
            arr = arr[idx]
        assert not isinstance(arr[last], list)
        arr[last] = value

    def __repr__(self) -> str:
        return f"FuncN(N={self.N}, K={self.K}, body={self.body})"

    def __eq__(self, other: 'FuncN') -> bool:
        return (self.N == other.N and self.K == other.K
                and self.body == other.body)

    def __lt__(self, other: 'FuncN'):
        assert self.N == other.N, (self.N, other.N)
        assert self.K == other.K, (self.K, other.K)
        self_reval = reval(self.body)
        other_reval = reval(other.body)
        assert len(self_reval) == len(other_reval)
        for i in range(len(self_reval)):
            if self_reval[i] is None:
                return False
            if other_reval[i] is None:
                return False
            if self_reval[i] < other_reval[i]:
                return True
            if self_reval[i] > other_reval[i]:
                return False

class Func1(FuncN):
    def __init__(self, K: int) -> None:
        self.body: list[int|None]
        super().__init__(1, K)

    @classmethod
    def copy(cls, of: 'Func1'):
        self = cls(of.K)
        self.inplace_copy(of)
        return self

    def isCorrect(self):
        return True

    def isSuitable(self) -> bool:
        if self(self) == self:
            return True
        if isPrimePermutation(self.body):
            return True
        return False

    def __repr__(self) -> str:
        return self.body.__repr__()

    def __call__(self, obj):
        if isinstance(obj, Func1):
            ans = Func1(self.K)
            ans.body = [
                obj.body[i] if i is not None else None
                    for i in self.body
            ]
            return ans
        if isinstance(obj, int):
            assert 0 <= obj < len(self.body)
            return self.body[obj]
        assert False

    def __eq__(self, value: 'Func1') -> bool:
        return (self.K == value.K) and (self.body == value.body)

class Func2(FuncN):
    def __init__(self, K: int) -> None:
        self.body: list[list[int | None]]
        super().__init__(2, K)
        self.isVarOrder = False

    @classmethod
    def copy(cls, of: 'Func2'):
        self = cls(of.K)
        self.inplace_copy(of)
        self.isVarOrder = of.isVarOrder
        return self

    def isCorrect(self):
        if self.nextCoord == (0, 0):
            return True
        if not self.isVarOrder:
            for i in range(self.K):
                for j in range(self.K):
                    xij = self.body[i][j]
                    xji = self.body[j][i]
                    if xij is None or xji is None:
                        return True
                    if xij > xji:
                        return False
                    if xij < xji:
                        self.isVarOrder = True
                        return True
        return super().isCorrect()
    def isSuitable(self) -> bool:
        for i in range(self.K):
            val = self.body[i][i]
            assert val is not None
            if val != i:
                return False
        return True
    def __repr__(self) -> str:
        return self.body.__repr__()

