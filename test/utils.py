from src.kfuncs import Func1, Func2
from src.utils import canonicalTable, removeConjugates

def testIsomorphicFunctions(f1, f2, K=2, args=2):
    canon1 = canonicalTable(f1, args, K)
    canon2 = canonicalTable(f2, args, K)
    assert canon1 == canon2, (canon1, canon2)

def testNonIsomorphicFunctions(f1, f2, K=2, args=2):
    canon1 = canonicalTable(f1, args, K)
    canon2 = canonicalTable(f2, args, K)
    assert canon1 != canon2, (canon1, canon2)

def testCanonicalTable():
    testIsomorphicFunctions([0,0,0], [1,1,1], K=3, args=1)
    testNonIsomorphicFunctions([0,0,0], [0,0,2], K=3, args=1)

def testRemoveConjugates():
    # ans = removeConjugates([f1, f2])
    # assert len(ans) == 1, ans
    pass

def unitTestPackUnpack(func: Func1 | Func2):
    code = func.pack()
    func2 = type(func)(func.K).unpack(code)
    assert func.body == func2.body, (func.body, func2.body)

def unitTestUnpackPackArg1(code: int, K=2):
    func1 = Func1(K)
    func1.unpack(code)
    assert func1.pack() == code, (func1.pack(), code)

def unitTestUnpackPackArg2(code: int, K=2):
    func1 = Func2(K)
    func1.unpack(code)
    assert func1.pack() == code, (func1.pack(), code)

def testUnpackPack():
    for K in range(2, 4):
        for code in range(K**K):
            unitTestUnpackPackArg1(code, K=K)
    for K in range(2, 4):
        for code in range(K**(K**2)):
            unitTestUnpackPackArg2(code, K=K)

def tests():
    testCanonicalTable()
    testRemoveConjugates()
    testUnpackPack()

tests()