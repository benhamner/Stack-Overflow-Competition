import data_io
from datetime import datetime
from features import FeatureMapper, SimpleTransform
import pandas as pd
import psycopg2
import requests

def get_most_recent_questions(num_questions=50):
    r = requests.get("http://api.stackexchange.com/2.1/questions?page=1&pagesize=%d&order=desc&sort=activity&site=stackoverflow" % num_questions)
    recent_questions = r.json["items"]

    recent_questions = [q for q in recent_questions if "user_id" in q["owner"]]

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

        try:
            owner_creation_date = [user for user in users if user["user_id"] == raw_question["owner"]["user_id"]][0]["creation_date"]
            body_html = [question for question in questions_w_body if question["question_id"] == raw_question["question_id"]][0]["body"]
        except IndexError:
            continue

        raw_question["tags"].extend(["" for x in range(5)])

        question = { "PostId" : raw_question["question_id"]
                   , "PostCreationDate" : datetime.fromtimestamp(int(raw_question["creation_date"]))
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
    return data, questions

def copy_to_postgres(questions, prob_closed):
    conn = psycopg2.connect('dbname=stack user=postgres password=sx7%8rBSgB3SPuytB535')
    cur = conn.cursor()

    for question, prob in zip(questions, prob_closed):
        cur.execute("""SELECT COUNT(*)
                       FROM questions
                       WHERE post_id=%(PostId)s""",
                    question)
        res = cur.fetchone()
        print(res)
        if res[0]>0:
            continue
        question["close_likelihood"] = prob
        cur.execute("""INSERT INTO questions (post_id,
                                              post_creation_date,
                                              owner_user_id,
                                              owner_creation_date,
                                              reputation_at_post_creation,
                                              owner_undeleted_answer_count_at_post_time,
                                              title,
                                              body_html,
                                              tag1,
                                              tag2,
                                              tag3,
                                              tag4,
                                              tag5,
                                              close_likelihood)
                       VALUES (%(PostId)s,
                               %(PostCreationDate)s,
                               %(OwnerUserId)s,
                               %(OwnerCreationDate)s,
                               %(ReputationAtPostCreation)s,
                               %(OwnerUndeletedAnswerCountAtPostTime)s,
                               %(Title)s,
                               %(BodyMarkdown)s,
                               %(Tag1)s,
                               %(Tag2)s,
                               %(Tag3)s,
                               %(Tag4)s,
                               %(Tag5)s,
                               %(close_likelihood)s)
                    """, question)
    conn.commit()

def read_classify_save_loop():
    print("Getting the newest data")
    recent, questions = get_most_recent_questions()

    print("Loading the trained model")
    classifier = data_io.load_model("model.pickle")

    print("Making predictions")
    probs = classifier.predict_proba(recent)

    prob_closed = 1-probs[:,1]
    titles = [x for x in recent["Title"]]
    tuples = sorted(zip(titles, prob_closed), key=lambda x: x[1])

    for title, prob in tuples:
        print("%s, %f" % (title, prob))

    copy_to_postgres(questions, prob_closed)

def main():
    import sched, time
    s = sched.scheduler(time.time, time.sleep)
    def do_something(sc): 
        read_classify_save_loop()
        sc.enter(120, 1, do_something, (sc,))

    s.enter(120, 1, do_something, (s,))
    s.run()

if __name__=="__main__":
    read_classify_save_loop()