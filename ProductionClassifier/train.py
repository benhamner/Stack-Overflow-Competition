import data_io
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from features import FeatureMapper, SimpleTransform

def get_title(d):
    pickle.dump(d, open("d.pickle", "w"))
    return d.Title

def feature_extractor():
    features = [('Title-Bag of Words', 'Title', CountVectorizer(max_features=400)),
                ('Body-Bag of Words', 'BodyMarkdown', CountVectorizer(max_features=400)),
                ('Title-Character Count', 'Title', SimpleTransform(len)),
                ('Body-Character Count', 'BodyMarkdown', SimpleTransform(len)),
                ('OwnerUndeletedAnswerCountAtPostTime', 'OwnerUndeletedAnswerCountAtPostTime', SimpleTransform()),
                ('ReputationAtPostCreation', 'ReputationAtPostCreation', SimpleTransform())]
    combined = FeatureMapper(features)
    return combined

def get_pipeline():
    features = feature_extractor()
    steps = [("extract_features", features),
             ("classify", RandomForestClassifier(n_estimators=5, 
                                                 verbose=2,
                                                 n_jobs=-1      ))]
    return Pipeline(steps)

def main():
    print("Reading in the training data")
    train = data_io.get_train_df()

    print("Extracting features and training")
    classifier = get_pipeline()
    classifier.fit(train, train["OpenStatus"])

    print("Saving the classifier")
    data_io.save_model(classifier, "model.pickle")
    model = data_io.load_model("model.pickle")

if __name__=="__main__":
    main()