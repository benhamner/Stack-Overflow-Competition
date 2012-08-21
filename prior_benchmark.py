import competition_utilities as cu
import numpy as np

def main():
    priors = cu.get_priors("train.csv")
    num_samples = len(cu.get_dataframe("public_leaderboard.csv"))
    predictions = np.kron(np.ones((num_samples,1)), priors)
    cu.write_submission("prior_benchmark.csv", predictions)

if __name__=="__main__":
    main()