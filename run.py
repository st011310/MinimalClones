import test
from src import main

K = 4

main(K=K, filenames=[f"./output/E{K}_{i+1}.txt" for i in range(2)], verbose=True)
