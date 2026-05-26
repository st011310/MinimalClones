from libs.branch_bound import BranchAndBound

import pandas as pd
import datetime, os

def addStats(filename: str, **kwargs):
    if not os.path.exists(filename):
        pd.DataFrame(columns=list(kwargs.keys())).to_csv(filename, index=False)
    df = pd.read_csv(filename, encoding='utf8', index_col=False)
    df.loc[len(df)] = kwargs
    df.to_csv(filename, index=False)