import test
from src import main

K = 4

main(K=K, filenames=[f"./output/E{K}_{i}.txt" for i in range(1)], verbose=True)
