from libs.branch_bound import BranchAndBound
from .kfuncs import Func1
from .utils import removeConjugates

def main(K: int, filenames: list[str], verbose = False):
    funcs =[Func1]
    for i in range(min(1, len(filenames))):
        t = funcs[i]
        solver = BranchAndBound(t(K), verbose=verbose)
        solver.solve()
        solver.entities = removeConjugates(
            [t(K).unpack(num).body for num in  solver.entities],
            k=K, n=i+1
        )
        solver.save_transform(filenames[i], lambda f: "".join([str(num) for num in f]))
