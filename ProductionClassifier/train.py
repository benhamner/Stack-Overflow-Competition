import data_io
from features import FeatureMapper, SimpleTransform
import numpy as np
from pagedown import PagedownToHtml
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

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
             ("classify", RandomForestClassifier(n_estimators=50, 
                                                 verbose=2,
                                                 n_jobs=-1,
                                                 min_samples_split=30))]
    return Pipeline(steps)

def main():
    markdown = PagedownToHtml()

    print("Reading in the training data")
    train = data_io.get_train_df()
    for i in train.index:
        train["BodyMarkdown"][i] = markdown.convert(train["BodyMarkdown"][i])

    print("Extracting features and training")
    classifier = get_pipeline()
    classifier.fit(train, train["OpenStatus"])

    print("Saving the classifier")
    data_io.save_model(classifier, "model.pickle")
    model = data_io.load_model("model.pickle")

if __name__=="__main__":
    main()