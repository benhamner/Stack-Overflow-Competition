import flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import flask.ext.restless

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgres1234@/stack'
db = SQLAlchemy(app)

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

print(Questions.__tablename__)

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Questions, methods=['GET'], results_per_page=1000)
app.run()
