"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask,render_template
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

DB = SQLAlchemy(APP)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return 'Record data and values'

api = openaq.OpenAQ()

status, body = api.measurements(city='Los Angeles', parameter="pm25")
# Create a empty data
data_and_value=[]
# create a loop
for result in body["results"]:
    value=result["value"]
    utc_date=result["date"]['utc']
    data_and_value.append((str(utc_date),value))

@APP.route('/')
def root():
    my_table= data_and_value

    return render_template("base.html", title="City", list=my_table)

@APP.route('/page')
def page():
	top10 = Record.query.filter(Record.values >= 10).all()
	return render_template('base.html', top10=top10)

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO 

    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    # create a loop
    for result in body["results"]:
        value=result["value"]
        utc_date=result["date"]['utc']
        new_entry=Record(datetime=utc_date, value=value)

    # Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'

# To test and verify, you can execute`FLASK_APP=aq_dashboard.py flask shell`:
#>>> from aq_dashboard import Record
# >>> Record.query.all()[:5]