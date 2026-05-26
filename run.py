import test
from src import main
# from src.brout_force import main

K = 3

main(K=K, filenames=[f"./output/E{K}_{i+1}.txt" for i in range(2)], verbose=True)

# N = 2
# main(K=K, N=N, filename=f"./output/_.txt")
