from typing import Any

from copy import deepcopy
from libs.branch_bound import Entity
from .utils import isPrimePermutation, getNewSingletonElement, nextTuple, prevTuple

class Func1(Entity):
    def __init__(self, K: int) -> None:
        super().__init__()
        self.K = K
        self.body: list[int|None] = [None] * K
        self.nextCoord = 0
        self.knownElems = set()
        self.allElems = set(range(K))
    def branches(self):
        knownElems = self.knownElems | {self.nextCoord}
        newElemSet = getNewSingletonElement(knownElems, self.allElems)
        for i in knownElems | newElemSet:
            obj = Func1(self.K)
            obj.body = deepcopy(self.body)
            obj.body[self.nextCoord] = i
            obj.nextCoord = self.nextCoord + 1
            obj.knownElems = knownElems | {i}
            yield obj


    def isComplete(self) -> bool:
        return self.body[-1] is not None

    def isCorrect(self):
        return True

    def pack(self) -> int:
        assert self.isComplete()
        ans = 0
        for i in self.body:
            assert i is not None
            ans = ans * self.K + i
        return ans

    def unpack(self, code: int):
        n = len(self.body)
        for i in range(n):
            self.body[n - i - 1] = code % self.K
            code //= self.K
        return self

    def isSuitable(self) -> bool:
        if self(self) == self:
            return True
        if isPrimePermutation(self.body):
            return True
        return False

    def __repr__(self) -> str:
        return self.body.__repr__()

    def __call__(self, obj: 'Func1') -> 'Func1':
        ans = Func1(self.K)
        ans.body = [obj.body[i] for i in self.body]
        return ans

    def __eq__(self, value: 'Func1') -> bool:
        return (self.K == value.K) and (self.body == value.body)

class Func2(Entity):
    def __init__(self, K: int) -> None:
        super().__init__()
        self.K = K
        self.body: list[list[int|None]] = [
            [None for _ in range(K)] for _ in range(K)]
        self.nextCoord = (0, 0)
        self.knownElems: set[int] = set()
        self.allElems = set(range(K))
        self.isVarOrder = False
    def branches(self):
        if self.nextCoord[0] == self.nextCoord[1]:
            i = self.nextCoord[0]
            obj = Func2(self.K)
            obj.body = deepcopy(self.body)
            obj.body[i][i] = i
            obj.nextCoord = nextTuple(self.nextCoord, self.K)
            obj.knownElems = self.knownElems | {i}
            obj.isVarOrder = self.isVarOrder
            yield obj
            return
        knownElems = self.knownElems | set(self.nextCoord)
        newElemSet = getNewSingletonElement(knownElems, self.allElems)
        for i in knownElems | newElemSet:
            x = self.nextCoord[0]
            y = self.nextCoord[1]
            obj = Func2(self.K)
            obj.body = deepcopy(self.body)
            obj.body[x][y] = i
            obj.nextCoord = nextTuple(self.nextCoord, self.K)
            obj.knownElems = knownElems | {i}
            obj.isVarOrder = self.isVarOrder
            yield obj

    def isComplete(self) -> bool:
        return self.body[-1][-1] is not None

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
        return True

    def pack(self) -> int:
        assert self.isComplete()
        ans = 0
        for row in self.body:
            for i in row:
                assert i is not None
                ans = ans * self.K + i
        return ans

    def unpack(self, code: int):
        n = len(self.body)
        for i in range(n):
            row = []
            for j in range(n):
                row.append(code % self.K)
                code //= self.K
            self.body[n - i - 1] = row[::-1]
        return self

    def isSuitable(self) -> bool:
        for i in range(self.K):
            val = self.body[i][i]
            assert val is not None
            if val != i:
                return False
        return True

    def __call__(self, obj1, obj2):
        if isinstance(obj1, int):
            resFunc = Func1(self.K)
            resFunc.body = self.body[obj1]
            return resFunc(obj2)
        if isinstance(obj1, Func1):
            resFunc = Func2(self.K)
            resFunc.body = [self.body[i] for i in obj1.body]
            return resFunc(obj2)


    def __repr__(self) -> str:
        return self.body.__repr__()

    def __eq__(self, value: 'Func2') -> bool:
        return (self.K == value.K) and (self.body == value.body)

