
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

def get_histogram(solution_column, predictions):
    these_predictions = [p for s,p in zip(solution_column, predictions) if s==1]
    return np.histogram(these_predictions, bins=np.linspace(0,1,51), density=True)

def main():
    stack_path = os.path.join(os.environ["DataPath"], "StackOverflow")
    solution = pd.read_csv(os.path.join(stack_path, "Results", "PrivateLeaderboardSolution.csv"))
    first_place = pd.read_csv(os.path.join(stack_path, "Results", "1stPrivate.csv"))

    columns = ["not a real question",
               "not constructive",
               "off topic",
               "open",
               "too localized"]

    plt.figure(figsize = (8,5))

    for col in columns:
        density, bins = get_histogram(solution[col], first_place["open"])
        centers = (bins[1:]+bins[:-1])/2
        plt.plot(centers, density)
    plt.legend(columns, 0)
    plt.xlabel("Predicted Probability Question is Open", fontsize=14)
    plt.ylabel("Density", fontsize=14)
    plt.title("1st Place Prediction Distributions", fontsize=16)
    plt.savefig(os.path.join(stack_path, "Results", "Plots", "1st Place Prediction Distributions.png"), dpi=(640/3))

if __name__=="__main__":
    main()