from tqdm import tqdm

from libs.branch_bound import BranchAndBound
from .kfuncs import Func1, Func2, FuncN
from .stats import addStats
from .utils import removeConjugates

import datetime, os

SOLVE_INFO_FILE = "solve_info.csv"


def main(K: int, filenames: list[str], verbose = False):
    funcs: list[type[Func1 | Func2]] = [Func1, Func2]
    for i in range(min(2, len(filenames))):
        if i == 0:
            continue
        t = funcs[i]
        N = i+1
        solver = BranchAndBound(t(K), verbose=verbose)
        tStart = datetime.datetime.now()
        solver.solve()
        tEnd = datetime.datetime.now()
        addStats(start=tStart, end=tEnd, delta=tEnd-tStart, args_num=N,
                 K=K, funcs_found=len(solver.entityHashes), comment="",
                 filename=os.path.join("output", SOLVE_INFO_FILE))
        print("Remove duplicates...")
        tables = removeConjugates(
            [t(K).unpack(num).body for num in  solver.entityHashes],
            k=K, n=N
        )
        if False:
            print("Filter minimum...")
            entities = list[FuncN]()
            for table in tqdm(tables, desc="Подготовка"):
                func = FuncN(K=K, N=N)
                func.body = table
                entities.append(func)
            entities.sort(key = lambda f: len(set(f.reval())))
            res = []
            minimals = set[int]()
            for entity in tqdm(entities):
                if not entity.isMinimal(minimals):
                    continue
                minimals.add(entity.pack())
                res.append(entity.body)
        else:
            res = tables
        print("Sorting...")
        res.sort()
        solver.save(filenames[i], res)
