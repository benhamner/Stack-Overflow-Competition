import data_io
from datetime import datetime
from features import FeatureMapper, SimpleTransform
import pandas as pd
import requests

def get_most_recent_questions(num_questions=30):
    r = requests.get("http://api.stackexchange.com/2.1/questions?page=1&pagesize=%d&order=desc&sort=activity&site=stackoverflow" % num_questions)
    recent_questions = r.json["items"]

    question_ids = [str(question["question_id"]) for question in recent_questions]
    user_ids = [str(question["owner"]["user_id"]) for question in recent_questions]

    question_ids_str = ";".join(question_ids)
    user_ids_str = ";".join(user_ids)

    r = requests.get("https://api.stackexchange.com/2.1/users/%s/answers?order=desc&sort=activity&site=stackoverflow" % user_ids_str)
    user_answers = r.json["items"]

    r = requests.get("https://api.stackexchange.com/2.1/users/%s?order=desc&sort=reputation&site=stackoverflow" % user_ids_str)
    users = r.json["items"]

    r = requests.get("http://api.stackoverflow.com/1.1/questions/%s?body=true" % question_ids_str)
    questions_w_body = r.json["questions"]

    questions = []

    for raw_question in recent_questions:
        num_user_answers = len([answer for answer in user_answers if answer["owner"]["user_id"] == raw_question["owner"]["user_id"]])
        print(num_user_answers)

        owner_creation_date = [user for user in users if user["user_id"] == raw_question["owner"]["user_id"]][0]["creation_date"]
        body_html = [question for question in questions_w_body if question["question_id"] == raw_question["question_id"]][0]["body"]

        raw_question["tags"].extend(["" for x in range(5)])

        question = { "PostCreationDate" : datetime.fromtimestamp(int(raw_question["creation_date"]))
                   , "OwnerUserId" : raw_question["owner"]["user_id"]
                   , "OwnerCreationDate" : datetime.fromtimestamp(int(owner_creation_date))
                   , "ReputationAtPostCreation" : raw_question["owner"]["reputation"]
                   , "OwnerUndeletedAnswerCountAtPostTime" : str(num_user_answers)
                   , "Title" : raw_question["title"]
                   , "BodyMarkdown" : body_html
                   , "Tag1" : raw_question["tags"][0]
                   , "Tag2" : raw_question["tags"][1]
                   , "Tag3" : raw_question["tags"][2]
                   , "Tag4" : raw_question["tags"][3]
                   , "Tag5" : raw_question["tags"][4]
                   }

        questions.append(question)

    questions_for_conversion_to_df = {key: [] for key in questions[0].keys()}
    for q in questions:
        for k in q.keys():
            questions_for_conversion_to_df[k].append(q[k])
    data = pd.DataFrame(questions_for_conversion_to_df)
    return data

def main():
    print("Getting the newest data")
    recent = get_most_recent_questions()

    print("Loading the trained model")
    classifier = data_io.load_model("model.pickle")

    print("Making predictions")
    probs = classifier.predict_proba(recent)

    prob_open = probs[:,1]
    titles = [x for x in recent["Title"]]
    tuples = sorted(zip(titles, prob_open), key=lambda x: x[1])

    for title, prob in tuples:
        print("%s, %f" % (title, prob))

if __name__=="__main__":
    main()