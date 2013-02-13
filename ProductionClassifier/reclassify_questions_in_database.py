import data_io
from datetime import datetime
from features import FeatureMapper, SimpleTransform
import os
import pandas as pd
import psycopg2
import re
import requests

def connect_to_postgres():
    db_string = os.environ["DATABASE_URL"]
    db_info = re.findall(r"postgres://(\S+):(\S+)@(\S+):(\S+)/(\S+)", db_string)[0]
    db_user, db_pass, db_host, db_port, db_name = db_info

    conn = psycopg2.connect(database=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)
    return conn

def update_postgres_close_likelihood(question_ids, prob_closed):
    print("Making second connection")
    conn = connect_to_postgres()
    print("Made second connection")
    cur = conn.cursor()

    print("Got cursor")

    cur.executemany("""UPDATE questions
                       SET close_likelihood = %s
                       WHERE post_id = %s
                    """, [(str(prob), str(question_id)) for question_id, prob in zip(question_ids, prob_closed)])

    print("Ran executemany")

    conn.commit()

    print("committing")

    conn.close()
    print("closing")

def get_questions_from_postgres():
    conn = connect_to_postgres()
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