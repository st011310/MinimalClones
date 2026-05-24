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

def tests():
    testCanonicalTable()
    testRemoveConjugates()

tests()