from flask import Flask, render_template, url_for, redirect 
from forms import RegistrationForm, LoginForm, PortfolioForm
from flask_sqlalchemy import SQLAlchemy
import json
import forms

app = Flask(__name__)

app.config['SECRET_KEY'] = 'QUWU7Ax94jCsknrT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Creates a User table in database with appropriate columns 
class User(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(50), unique=True, nullable=False)
   password = db.Column(db.String(50), nullable=False)

   def __repr__(self):
       return f"User('{self.username}')"

# Creates a Portfolio table in database with appropriate columns 
class Portfolio(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   international = db.Column(db.Integer, nullable=False)
   domestic = db.Column(db.Integer, nullable=False)
   bonds = db.Column(db.Integer, nullable=False)
   money_market = db.Column(db.Integer, nullable=False)

   def __repr__(self):
       return f"User('{self.user_id}', '{self.domestic}')"



with open('presets.json', 'r') as input:
    preset_data = json.load(input)

@app.route('/')
@app.route('/home')
def home(): 
    return render_template('home.html')

@app.route("/presets")
def presets():
    return render_template('presets.html', title='Base Data', preset_data = preset_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # create instance of a user with info entered from Registration form
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/enterport', methods=['GET', 'POST'])
def enter_port():
    form = PortfolioForm()
    if form.validate_on_submit():
        # create instance of a portfolio info with info entered from form
        data = Portfolio(domestic=form.domestic.data, international=form.international.data, money_market=form.money_market.data, bonds=form.bonds.data)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('userportfolio.html', title='Enter Your Portfolio', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        return redirect('userDashboard')
    return render_template('login.html', form = form)

@app.route('/userDashboard')
def userDashboard():
    return render_template('userDashboard.html')


# run on debug mode to not re-start server after changes
if __name__ == '__main__':

    app.run(debug = True)
