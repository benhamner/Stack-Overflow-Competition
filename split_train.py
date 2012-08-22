import competition_utilities as cu
import csv
import datetime
import os

def main():
    data = cu.get_dataframe("train.csv")
    data = data.sort_index(by="PostCreationDate")

    header = cu.get_header("train.csv")
    cutoff = datetime.datetime(2012, 7, 18)

    data[data["PostCreationDate"] < cutoff].to_csv(os.path.join(cu.data_path, "train-A.csv"), index=False)
    data[data["PostCreationDate"] >= cutoff].to_csv(os.path.join(cu.data_path, "train-B.csv"), index=False)

if __name__=="__main__":
    main()
