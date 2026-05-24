from typing import Any

from libs.branch_bound import Entity
from .utils import isPrimePermutation

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
        if len(self.allElems) != len(knownElems):
            newElem = min(self.allElems - knownElems)
            newElemSet = {newElem}
        else:
            newElemSet = set()
        for i in knownElems | newElemSet:
            obj = Func1(self.K)
            obj.body = self.body[:]
            obj.body[self.nextCoord] = i
            obj.nextCoord = self.nextCoord + 1
            obj.knownElems = self.knownElems | {i} | {self.nextCoord}
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
        assert self.isComplete()
        n = len(self.body)
        for i in range(n):
            self.body[n - i - 1] = code % self.K
            code //= self.K

    def isSuitable(self) -> bool:
        if self(self) == self:
            return True
        if isPrimePermutation(self.body):
            return True
        return False

    def isMin(self, num):
        self.unpack(num)
        return True

    def __repr__(self) -> str:
        return self.body.__repr__()

    def __call__(self, obj: 'Func1') -> 'Func1':
        ans = Func1(self.K)
        ans.body = [obj.body[i] for i in self.body]
        return ans

    def __eq__(self, value: 'Func1') -> bool:
        return (self.K == value.K) and (self.body == value.body)

