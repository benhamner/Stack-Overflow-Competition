import data_io
from datetime import datetime
from features import FeatureMapper, SimpleTransform
import pandas as pd
import psycopg2
import requests

client_secret = "05Ksix0PLYhl5FMvlS)LLw(("
key = "jsRdHLGT2S57bRWf0XqssA(("

def dict_to_url_options(opts_dict):
    url_options = []
    for key in opts_dict:
        url_options.append("%s=%s" % (key, str(opts_dict[key])))
    return "&".join(url_options)

def get_recent_questions(num_questions=100):
    opts = { "page" : 1
           , "pagesize" : num_questions
           , "order" : "desc"
           , "sort" : "creation"
           , "site" : "stackoverflow"
           , "client_secret" : client_secret
           , "key" : key
           }
    url_opts = dict_to_url_options(opts)
    r = requests.get("http://api.stackexchange.com/2.1/questions?%s"
                      % url_opts)
    raw_questions = r.json["items"]
    raw_questions_with_user = [q for q in raw_questions
                               if "user_id" in q["owner"]]
    print("%d/%d" % (len(raw_questions), len(raw_questions_with_user)))
    return raw_questions_with_user

def get_user_ids_from_questions(raw_questions):
    return [str(q["owner"]["user_id"]) for q in raw_questions]
    
def get_question_ids_from_questions(raw_questions):
    return [str(q["question_id"]) for q in raw_questions]

def get_user_answers(user_ids, page=1):
    user_ids_str = ";".join(user_ids)
    opts = { "page" : page
           , "pagesize" : 100
           , "order" : "desc"
           , "sort" : "activity"
           , "site" : "stackoverflow"
           , "client_secret" : client_secret
           , "key" : key
           }
    url_opts = dict_to_url_options(opts)
    r = requests.get("https://api.stackexchange.com/2.1/users/%s/answers?%s"
                     % (user_ids_str, url_opts))
    user_answers = r.json["items"]
    if r.json["has_more"]:
        user_answers.extend(get_user_answers(user_ids, page=page+1))
    return user_answers

def get_users(user_ids):
    user_ids_str = ";".join(user_ids)
    opts = { "page" : 1
           , "pagesize" : 100
           , "order" : "desc"
           , "sort" : "reputation"
           , "site" : "stackoverflow"
           , "client_secret" : client_secret
           , "key" : key
           }
    url_opts = dict_to_url_options(opts)
    r = requests.get("https://api.stackexchange.com/2.1/users/%s?%s"
                     % (user_ids_str, url_opts))
    users = r.json["items"]
    return users 


def get_question_bodies(question_ids):
    question_ids_str = ";".join(question_ids)
    opts = { "pagesize" : 100
           , "body" : "true"
           }    
    url_opts = dict_to_url_options(opts)
    r = requests.get("http://api.stackoverflow.com/1.1/questions/%s?%s"
                     % (question_ids_str, url_opts))
    question_bodies = r.json["questions"]
    return question_bodies

def scrape_pipeline(num_questions=100):
    raw_questions_with_user = get_recent_questions(num_questions)

    user_ids = get_user_ids_from_questions(raw_questions_with_user)    
    question_ids = get_question_ids_from_questions(raw_questions_with_user)

    user_answers = get_user_answers(user_ids, page=1)
    users = get_users(user_ids)
    question_bodies = get_question_bodies(question_ids)

    questions = []

    for raw_question in raw_questions_with_user:
        num_user_answers = len([answer for answer in user_answers if answer["owner"]["user_id"] == raw_question["owner"]["user_id"]])
        #print(num_user_answers)

        try:
            owner_creation_date = [user for user in users if user["user_id"] == raw_question["owner"]["user_id"]][0]["creation_date"]
            body_html = [question for question in question_bodies if question["question_id"] == raw_question["question_id"]][0]["body"]
        except IndexError:
            print("Index Error: Question %d" % raw_question["question_id"])
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

    print(len(raw_questions_with_user))
    print(len(questions))

    questions_for_conversion_to_df = {key: [] for key in questions[0].keys()}
    for q in questions:
        for k in q.keys():
            questions_for_conversion_to_df[k].append(q[k])
    data = pd.DataFrame(questions_for_conversion_to_df)
    return data, questions

def copy_to_postgres(questions):
    conn = psycopg2.connect('dbname=stack user=postgres password=sx7%8rBSgB3SPuytB535')
    cur = conn.cursor()

    cnt_already_in = 0

    for question in questions:
        cur.execute("""SELECT COUNT(*)
                       FROM questions
                       WHERE post_id=%(PostId)s""",
                    question)
        res = cur.fetchone()
        if res[0]>0:
            cnt_already_in += 1
            continue
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
                                              tag5)
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
                               %(Tag5)s)
                    """, question)
    conn.commit()
    print("%d/%d Already in database" % (cnt_already_in, len(questions)))

def main():
    recent, questions = scrape_pipeline()
    copy_to_postgres(questions)

if __name__=="__main__":
    main()