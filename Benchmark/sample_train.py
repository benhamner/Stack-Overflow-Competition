import competition_utilities as cu
import csv
import os
import random

def reservoir_sample(generator, num_samples):
    sample = []
    enum = enumerate(generator)

    while len(sample) < num_samples:
        i, a = enum.next()
        sample.append(a)
    random.shuffle(sample)

    for i, a in enum:
        r = random.randint(0,i)
        if r < num_samples:
            sample[r]=a

    return sample

def sample_train(input_file):
    closed_count = cu.get_closed_count(input_file)
    sample = reservoir_sample(cu.iter_open_questions(input_file), closed_count)
    sample.extend(cu.iter_closed_questions(input_file))
    random.shuffle(sample)
    header = cu.get_header(input_file)
    return header, sample

def main():
    header, sample = sample_train(os.path.join(cu.data_path, "train.csv"))
    cu.write_sample("train-sample1.csv", header, sample)

    header, sample = sample_train(os.path.join(cu.data_path, "train-A.csv"))
    save_sample("train-A-sample1.csv", header, sample)

if __name__=="__main__":
    main()