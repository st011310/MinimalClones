from copy import deepcopy
from itertools import product, permutations
from libs.branch_bound import Entity
from .utils import (isPrimePermutation, getNewSingletonElement,
                    nextTuple, make_nested,
                    decodeTuple, tupleIterator)

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
        self.maxDeaph = K**N
        self._flat_cache = None

    def reval(self):
        if not self._flat_cache:
            self._flat_cache = [
                self[coord] for coord in tupleIterator(n=self.N, k=self.K)
            ]
        return self._flat_cache

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
        return all(v is not None for v in self.reval())

    def isCorrect(self, max_iteration = None):
        '''Функция минимальна среди порождающих функций'''
        if self.N <= 1:
            return True
        if max_iteration is None:
            if self.deaph <= 10:
                max_iteration = 100
            else:
                max_iteration = 10
        i = 0
        for func in self.getCloneIterator():
            if max_iteration < 0:
                break
            max_iteration -= 1
            i += 1
            if func < self:
                return False
        return True

    def isSuitable(self) -> bool:
        """Проверяем минимальность функции в своём клоне"""
        for func in self.getCloneIterator():
            if func < self:
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

    def selfApply(self) -> 'FuncN':
        """
        Самоподстановка: f̃(x) = f( f(x), …, f(x) ).
        """
        return self.compose(*([self] * self.N))

    def pack(self) -> int:
        assert self.isComplete()
        ans = 0
        for i in range(self.K ** self.N):
            coord = decodeTuple(i, self.N, self.K)
            dig = self[coord]
            assert dig is not None
            ans = ans * self.K + dig
        return ans

    def unpack(self, code: int):
        for i in range(self.K ** self.N):
            coord = decodeTuple(self.K ** self.N - 1 - i, self.N, self.K)
            self[coord] = code % self.K
            code //= self.K
        return self

    def getClone(self, stop_on = set[int]()):
        trivial_clone = {}
        for i in range(self.N):
            xi = FuncN(self.N, self.K)
            for coords in tupleIterator(self.K, self.N):
                xi[coords] = coords[i]
            trivial_clone[xi.pack()] = xi
        clone = {}
        for funcs in permutations(trivial_clone.values()):
            new_func = self.compose(*funcs)
            code = new_func.pack()
            clone[code] = new_func
            if code in stop_on:
                return {code:new_func}
        cur_len = 0
        while len(clone) != cur_len:
            cur_len = len(clone)
            for funcs in product(clone.values(), repeat=self.N):
                new_func = self.compose(*funcs)
                code = new_func.pack()
                clone[code] = new_func
                if code in stop_on:
                    return {code:new_func}
        return clone

    def getCloneIterator(self):
        trivial_clone = {}
        for i in range(self.N):
            xi = FuncN(self.N, self.K)
            for coords in tupleIterator(self.K, self.N):
                xi[coords] = coords[i]
            trivial_clone[xi.pack()] = xi
        clone = set()
        for funcs in permutations(trivial_clone.values()):
            new_func = self.compose(*funcs)
            if new_func in clone:
                continue
            clone.add(new_func)
            yield new_func
        cur_len = 0
        clone.add(None)
        while len(clone) != cur_len:
            cur_len = len(clone)
            for funcs in product(clone, repeat=self.N):
                new_func = self.compose(*funcs)
                if new_func in clone:
                    continue
                clone.add(new_func)
                yield new_func

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

    def __hash__(self) -> int:
        return sum(i for i in self.reval() if i is not None)

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
        self_reval = self.reval()
        other_reval = other.reval()
        assert len(self_reval) == len(other_reval)
        for s, o in zip(self_reval, other_reval):
            if s is None:
                return False
            if o is None:
                return False
            if s < o:
                return True
            if s > o:
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
            for i, j in tupleIterator(k=self.K,n=self.N):
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

