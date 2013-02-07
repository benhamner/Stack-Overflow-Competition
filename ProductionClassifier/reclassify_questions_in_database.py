import data_io
from datetime import datetime
from features import FeatureMapper, SimpleTransform
import pandas as pd
import psycopg2
import requests

def update_postgres_close_likelihood(question_ids, prob_closed):
    conn = psycopg2.connect('dbname=stack user=postgres password=sx7%8rBSgB3SPuytB535')
    cur = conn.cursor()

    for question_id, prob in zip(question_ids, prob_closed):
        cur.execute("""UPDATE questions
                       SET close_likelihood = %s
                       WHERE post_id = %s
                    """, [str(prob), str(question_id)])
    conn.commit()

def get_questions_from_postgres():
    conn = psycopg2.connect('dbname=stack user=postgres password=sx7%8rBSgB3SPuytB535')
    cur = conn.cursor()
    cur.execute("""SELECT post_id,
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
                          tag5
                   FROM questions
                """)
    res = cur.fetchall()
    conn.close()
    df = pd.DataFrame(res, columns=["PostId", 
                                    "PostCreationDate",
                                    "OwnerUserId",
                                    "OwnerCreationDate",
                                    "ReputationAtPostCreation",
                                    "OwnerUndeletedAnswerCountAtPostTime",
                                    "Title",
                                    "BodyMarkdown",
                                    "Tag1",
                                    "Tag2",
                                    "Tag3",
                                    "Tag4",
                                    "Tag5"])
    return df

def reclassify():
    print("Getting the questions in the database")
    questions = get_questions_from_postgres()
    print("%d questions retrieved" % len(questions))

    print("Loading the trained model")
    classifier = data_io.load_model("model.pickle")

    print("Making predictions")
    probs = classifier.predict_proba(questions)

    prob_closed = 1-probs[:,1]

    update_postgres_close_likelihood(questions["PostId"], prob_closed)

def main():
    reclassify()

if __name__=="__main__":
    main()