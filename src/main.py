from libs.branch_bound import BranchAndBound
from .kfuncs import Func1
from .utils import removeIsomorphicFunctions

def main(K: int, filenames: list[str], verbose = False):
    funcs =[Func1]
    for i in range(min(1, len(filenames))):
        t = funcs[i]
        solver = BranchAndBound(t(K), verbose=verbose)
        solver.solve()
        solver.entities = removeIsomorphicFunctions(solver.entities)

        solver.save(filenames[i])
