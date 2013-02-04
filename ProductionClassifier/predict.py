import data_io
from features import FeatureMapper

def main():
    print("Reading the private leaderboard file")
    test = data_io.get_test_df()

    print("Loading the trained model")
    classifier = data_io.load_model("model.pickle")

    print("Making predictions")
    probs = classifier.predict_proba(test)
    print(probs)

if __name__=="__main__":
    main()