from numpy import ndarray

from itertools import product, permutations
from libs.branch_bound import Entity
from .utils import (isPrimePermutation, getNewSingletonElement,
                    nextTuple, tupleIterator, encodeTuple, decodeTuple,
                    compose)

class FuncN(Entity):
    def __init__(self, N: int, K: int) -> None:
        super().__init__()
        self.N = N
        self.K = K
        self.allElems = set(range(K))
        self.body: list[int | None] = [None] * (K ** N)
        self.nextCoord = (0,) * N
        self.knownElems = set[int]()
        self.deaph = 0
        self.maxDeaph = K**N
        self._flat_index_cache = None
        self._flat_cache = None
        self._hash = None

    def _index_to_coord(self, index: int) -> tuple[int, ...]: # TODO: избыточный метод. Нужно удалить
        """Линейный индекс → кортеж координат."""
        coord = [0] * self.N
        for i in range(self.N - 1, -1, -1):
            coord[i] = index % self.K
            index //= self.K
        return tuple(coord)

    def reval(self):
        if not self._flat_index_cache:
            self._flat_index_cache = [
                encodeTuple(coord, self.K) for coord in tupleIterator(n=self.N, k=self.K)]
        for idx in self._flat_index_cache:
            yield self.body[idx]

    def inplace_copy(self, of: 'FuncN'):
        assert self.K == of.K
        assert self.N == of.N
        self.body = of.body.copy()
        self.nextCoord = nextTuple(of.nextCoord, of.K)
        self.deaph = of.deaph + 1
        self.knownElems = set()
        self._flat_index_cache = of._flat_index_cache
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
        return all(v is not None for v in self.body)

    def isCorrect(self, max_iteration=None):
        '''Функция минимальна среди порождающих функций'''
        if self.N <= 1:
            return True
        if max_iteration is None:
            max_iteration = 100 if self.deaph <= 10 else 10
        for func in self.getCloneIterator():
            if max_iteration < 0:
                break
            max_iteration -= 1
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
        h(x) = f(g₁(x), …, gₙ(x))
        """
        assert len(gs) == self.N
        assert all(g.N == self.N for g in gs if g is not None)
        h = FuncN(self.N, self.K)
        h.body = compose(self.body, [g.body if g else None for g in gs], self.N, self.K)
        return h

    def selfApply(self) -> 'FuncN':
        """
        Самоподстановка: f̃(x) = f( f(x), …, f(x) ).
        """
        return self.compose(*([self] * self.N))

    def pack(self) -> int:
        assert self.isComplete()
        ans = 0
        for val in self.body:
            assert val is not None
            ans = ans * self.K + val
        return ans

    def unpack(self, code: int):
        for i in range(len(self.body) - 1, -1, -1):
            self.body[i] = code % self.K
            code //= self.K
        return self

    def getClone(self, stop_on=set[int]()):
        trivial_clone = {}
        for i in range(self.N):
            xi = FuncN(self.N, self.K)
            for coord in tupleIterator(self.K, self.N):
                xi[coord] = coord[i]
            trivial_clone[xi.pack()] = xi

        clone = dict[int, FuncN]()
        for funcs in permutations(trivial_clone.values()):
            new_func = self.compose(*funcs)
            code = new_func.pack()
            clone[code] = new_func
            if code in stop_on:
                return {code: new_func}

        cur_len = 0
        while len(clone) != cur_len:
            cur_len = len(clone)
            for funcs in product(clone.values(), repeat=self.N):
                new_func = self.compose(*funcs)
                code = new_func.pack()
                clone[code] = new_func
                if code in stop_on:
                    return {code: new_func}
        return clone

    def getCloneIterator(self):
        trivial_clone = {}
        for i in range(self.N):
            xi = FuncN(self.N, self.K)
            for coord in tupleIterator(self.K, self.N):
                xi[coord] = coord[i]
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


    def isMinimal(self, knownMinimal=set[int]()):
        minimalClone = {self.pack()}
        for func in self.getCloneIterator():
            code = func.pack()
            if code in knownMinimal:
                return False
            clone = func.getClone(minimalClone | knownMinimal)
            isFound = len(clone) == 1
            if not isFound:
                return False
            else:
                minimalClone.add(code)
        return True

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = sum(v for v in self.body if v is not None)
        return self._hash

    def __getitem__(self, key):
        if not isinstance(key, (ndarray, tuple)) or len(key) != self.N:
            raise KeyError(f"Требуется кортеж длины {self.N}")
        if any(idx is None for idx in key):
            return None
        return self.body[encodeTuple(key, self.K)]

    def __setitem__(self, key, value):
        if not isinstance(key, (ndarray, tuple)) or len(key) != self.N:
            raise KeyError(f"Требуется кортеж длины {self.N}")
        idx = encodeTuple(key, self.K)
        oldValue = self.body[idx]
        if self._hash is not None:
            if oldValue is not None:
                self._hash -= oldValue
            if value is not None:
                self._hash += value
        self.body[idx] = value

    def __repr__(self) -> str:
        return f"FuncN(N={self.N}, K={self.K}, body={self.body})"

    def __eq__(self, other: 'FuncN') -> bool:
        return (self.N == other.N and self.K == other.K
                and self.body == other.body)

    def __lt__(self, other: 'FuncN'):
        assert self.N == other.N and self.K == other.K, (self.N, other.N)
        for s, o in zip(self.reval(), other.reval()):
            if s is None or o is None:
                return False
            if s < o:
                return True
            if s > o:
                return False
        return False


class Func1(FuncN):
    def __init__(self, K: int) -> None:
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
            for i, j in tupleIterator(k=self.K, n=self.N):
                xij = self[i, j]
                xji = self[j, i]
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
            val = self[i, i]
            assert val is not None
            if val != i:
                return False
        return True

