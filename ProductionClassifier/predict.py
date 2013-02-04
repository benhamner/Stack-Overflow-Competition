import data_io
from features import FeatureMapper, SimpleTransform
import ml_metrics as metrics

def main():
    print("Reading the private leaderboard file")
    test = data_io.get_test_df()

    print("Loading the trained model")
    classifier = data_io.load_model("model.pickle")

    print("Making predictions")
    probs = classifier.predict_proba(test)

    solution = data_io.get_private_leaderboard_solution_df()
    print("Open AUC: %0.6f" % metrics.auc(solution["open"], probs[:,1]))

if __name__=="__main__":
    main()