import flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import flask.ext.restless

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo= db.Column(db.Unicode)
    priority = db.Column(db.SmallInteger)
    due_date = db.Column(db.Date)

print(TodoItem.__tablename__)

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(TodoItem, methods=['GET'], results_per_page=1000)
app.run()
