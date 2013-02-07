import flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import flask.ext.restless

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sx7%8rBSgB3SPuytB535@/stack'
db = SQLAlchemy(app)

def fix_response(request):
    request.headers.add('Access-Control-Allow-Origin', '*')
    request.headers.add('Access-Control-Max-Age', '21600')
    request.headers.add('Access-Control-Allow-Methods', '')
    return request

app.process_response = fix_response

class Questions(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    post_id = db.Column(db.BigInteger)
    post_creation_date = db.Column(db.Date)
    owner_user_id = db.Column(db.BigInteger)
    owner_creation_date = db.Column(db.Date)
    reputation_at_post_creation = db.Column(db.BigInteger)
    owner_undeleted_answer_count_at_post_time = db.Column(db.BigInteger)
    title = db.Column(db.BigInteger)
    body_html = db.Column(db.BigInteger)
    tag1 = db.Column(db.BigInteger)
    tag2 = db.Column(db.BigInteger)
    tag3 = db.Column(db.BigInteger)
    tag4 = db.Column(db.BigInteger)
    tag5 = db.Column(db.BigInteger)
    close_likelihood = db.Column(db.Float)

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Questions, methods=['GET'], results_per_page=1000)
app.run()
