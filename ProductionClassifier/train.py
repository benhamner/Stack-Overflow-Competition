import data_io
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from features import FeatureMapper

def get_title(d):
    pickle.dump(d, open("d.pickle", "w"))
    return d.Title

def feature_extractor():
    features = [('title_bag_of_words', 'Title', CountVectorizer(max_features=50))]
    combined = FeatureMapper(features)
    return combined

def get_pipeline():
    features = feature_extractor()
    steps = [("extract_features", features),
             ("classify", RandomForestClassifier(n_estimators=5, 
                                                 verbose=2))]
    return Pipeline(steps)

def main():
    print("Reading in the training data")
    train = data_io.get_train_df()
    print(train)

    print("Extracting features and training")
    classifier = get_pipeline()
    #classifier.fit(train, [1 if x=="open" else 0 for x in train["OpenStatus"]])
    classifier.fit(train, train["OpenStatus"])
    print(dir(classifier))

    print("Saving the classifier")
    data_io.save_model(classifier, "model.pickle")
    model = data_io.load_model("model.pickle")

if __name__=="__main__":
    main()