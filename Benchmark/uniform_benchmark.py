import competition_utilities as cu
import numpy as np

def main():
    num_samples = len(cu.get_dataframe("public_leaderboard.csv"))
    predictions = np.kron(np.ones((num_samples,5)), np.array(0.2))
    cu.write_submission("uniform_benchmark.csv", predictions)

if __name__=="__main__":
    main()