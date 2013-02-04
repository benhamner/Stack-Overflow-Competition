from dateutil.parser import parse
import os
import pandas as pd
import pickle

status_dict = {"not a real question": 0,
               "not constructive": 1,
               "off topic": 2,
               "open": 3,
               "too localized": 4}

def open_status_converter(status):
    return status_dict[status]

def get_converters():
    return {"PostCreationDate": parse,
            "OwnerCreationDate": parse,
            "OpenStatus": open_status_converter}

def get_data_path():
    return os.path.join(os.environ["DataPath"],
                        "StackOverflow", "Transformed")

def get_train_df():
    train_path = os.path.join(get_data_path(), 
                              "train-sample_October_9_2012.csv")
    return pd.read_csv(train_path, converters=get_converters())

def get_test_df():
    train_path = os.path.join(get_data_path(), 
                              "private_leaderboard.csv")
    converters = get_converters()
    del(converters["OpenStatus"])
    return pd.read_csv(train_path, converters=converters)

def save_model(model, file_name):
    out_path = os.path.join(os.environ["DataPath"],
                            "StackOverflow",
                            "TrainedModels",
                            file_name)
    pickle.dump(model, open(out_path, "w"))

def load_model(file_name):
    in_path = os.path.join(os.environ["DataPath"],
                           "StackOverflow",
                           "TrainedModels",
                           file_name)
    return pickle.load(open(in_path))