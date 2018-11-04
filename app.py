#!/usr/bin/python3
from flask import Flask, url_for, render_template, request, flash, redirect, jsonify
from sqlalchemy.dialects.postgresql import *
from flask_sqlalchemy import *
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_marshmallow import Marshmallow
import json

if not os.environ.get('DATABASE_URL'):
    #Developement Database
    database_file = 'postgres://localhost/runnerbee'
    print('\n--CUSTOM ALERT--\nDatabase_URL is %s\n--END ALERT--' % database_file)
else:
    #Production Database
    database_file = os.environ['DATABASE_URL']
    print('\n--CUSTOM ALERT--\nDatabase_URL is %s\n--END ALERT--' % database_file)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '585g279b0br00rab66dyvwL0B62RDV;;S' #TEMPORARY KEY, CHANGE IN PRODUCTION

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

#Runs Table
class Run(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    date_posted = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    distance = db.Column(db.Float())
    run_time = db.Column(db.Integer())
    calories_burned = db.Column(db.Integer())

    def __repr__(self):
        return '<Run {}>'.format(self.distance)

# Marshmallow Schema

class RunSchema(ma.ModelSchema):
    class Meta:
        model = Run

#Forms
class AddEditRunForm(FlaskForm):
    distance = StringField('Distance (km)', validators=[DataRequired()])
    run_time = StringField('Run Time (minutes)', validators=[DataRequired()])
    calories_burned = StringField('Calories Burned', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Load stuff for Flask Shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Run': Run}

#Homepage route
@app.route('/index')
def go_index():
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    runs = Run.query.order_by(Run.date_posted.desc())
    return render_template('index.html', runs=runs)

#New Run Route
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddEditRunForm()
    run = Run()
    if form.validate_on_submit():
        run = Run(distance = form.distance.data, run_time = form.run_time.data, calories_burned = form.calories_burned.data)

        db.session.add(run)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_run.html', form = form, run = run)

@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete_run(id):
    Run.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_run(id):
    run = Run.query.filter_by(id=id).first_or_404()
    form = AddEditRunForm(obj=run)
    if form.validate_on_submit():
            run.distance = form.distance.data
            run.run_time = form.run_time.data
            run.calories_burned = form.calories_burned.data
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add_run.html', form=form, run = run)

@app.route('/dashboard')
def dashboard():
    runs = Run.query.order_by(Run.date_posted.desc())
    return render_template('dashboard.html', runs = runs)
