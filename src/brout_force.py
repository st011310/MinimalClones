from tqdm import tqdm

from .kfuncs import FuncN
from libs.branch_bound import BranchAndBound # Only for output

def removeConjugates(N: int, K: int):
    """
    functions: список таблиц истинности.
    Возвращает список представителей классов сопряжённости.
    """
    seen = {}
    result = []
    clones = {}
    tq = tqdm(FuncN(N, K).unpack(i) for i in range(K**K**N))
    tq.total = K**K**N
    for table in tq:
        if not table.isSuitable():
            continue
        code = table.pack()
        clones[code] = table.getMinimalClone(set(seen.keys()))
        key = min(clones[code])
        if key not in seen:
            seen[key] = table
            result.append(table)
        else:
            table2 = FuncN.copy(table)
            table2.unpack(key)
            clones[key] = table2.getMinimalClone()
            cond = len(clones[key]) < len(clones[code])
            cond = cond or (
                (len(clones[key]) == len(clones[code]))
                    and (table2.pack() < table.pack())
            )
            if cond:
                result.remove(seen[key])
                seen[key] = table
                result.append(table)
    return result


def main(K: int, N: int, filename: str):
    ans = removeConjugates(N, K)
    solver = BranchAndBound(None)
    solver.save(filename, ans)