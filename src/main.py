from libs.branch_bound import BranchAndBound
from .kfuncs import Func1, Func2
from .utils import removeConjugates, canonicalTable

def main(K: int, filenames: list[str], verbose = False):
    funcs: list[type[Func1 | Func2]] = [Func1, Func2]
    for i in range(min(2, len(filenames))):
        t = funcs[i]
        solver = BranchAndBound(t(K), verbose=verbose)
        solver.solve()
        entities = removeConjugates(
            [t(K).unpack(num).body for num in  solver.entityHashes],
            k=K, n=i+1
        )
        entities.sort()
        solver.save(filenames[i], entities)
        # if len(solver.entities) > 0 and len(solver.entities[0]) > 0:
        #     while isinstance(solver.entities[0][0], (list, tuple)):
        #         solver.entities = [sum(entity, []) for entity in solver.entities]
        # solver.save_transform(filenames[i], lambda f: "".join(map(str, f)))
