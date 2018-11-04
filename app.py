#!/usr/bin/python3
from flask import Flask, url_for, render_template, request, flash, redirect, jsonify
from sqlalchemy.dialects.postgresql import *
from flask_sqlalchemy import *
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
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
login = LoginManager(app)
login.login_view = 'login'

#Runs Table
class Run(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    date_posted = db.Column(db.DateTime(), index = True, default = datetime.utcnow)
    distance = db.Column(db.Float())
    run_time = db.Column(db.Integer())
    calories_burned = db.Column(db.Integer())

    def __repr__(self):
        return '<Run {}>'.format(self.distance)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

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

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

#Load stuff for Flask Shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Run': Run, 'User': User}

#User Loader
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


#Homepage route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/index')
def go_index():
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    runs = Run.query.order_by(Run.date_posted.desc())
    return render_template('index.html', runs=runs)

#New Run Route
@app.route('/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_run(id):
    Run.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def dashboard():
    runs = Run.query.order_by(Run.date_posted.desc())
    return render_template('dashboard.html', runs = runs)
