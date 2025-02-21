from flask import Flask, render_template, url_for, redirect, request, flash, session
from forms import RegistrationForm, LoginForm, PortfolioForm
from flask_sqlalchemy import SQLAlchemy
from flask_nav import Nav
from flask_nav.elements import Navbar, View
import json
import forms

app = Flask(__name__)

app.config['SECRET_KEY'] = 'QUWU7Ax94jCsknrT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

nav = Nav(app)

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
       return f"User('{self.user_id}', '{self.domestic}', '{self.international}', '{self.money_market}', '{self.bonds}')"


with open('presets.json', 'r') as input:
    preset_data = json.load(input)

@nav.navigation('the_nav')
def create_nav():
    if 'user' in session:
        return Navbar( 'Parity Portfolio',
                        View('Home', 'home'),
                        View('Dashboard', 'userDashboard'),
                        View('Portfolio Selections', 'presets'),
                        View('Add Portfolio', 'enter_port'),
                        View('Rebalance Portfolio', 'results'), 
                        View('Logout', 'logout')
        )

    else:
        return Navbar( 'Parity Portfolio',
                        View('Home', 'home'),
                        View('Register', 'register'),
                        View('Login', 'login')
        )

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

    if request.method == "GET":
        if 'user' in session:
            return render_template('userportfolio.html', title='Portfolio', form=form)
        else:
            flash("You must be logged in to access that page!")
            return redirect(url_for('login'))
    else:    
        if form.validate_on_submit():
            # create instance of a portfolio info with info entered from form
            data = Portfolio(user_id=session['userID'], domestic=form.domestic.data, international=form.international.data, money_market=form.money_market.data, bonds=form.bonds.data)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('home'))


@app.route('/results', methods=['GET', 'POST'])
def results():

    user_portfolio = Portfolio.query.filter_by(user_id=session['userID']).first()
    selected_preset = preset_data[1]
    preset_name = selected_preset['preset_name']

    domestic = user_portfolio.domestic
    international = user_portfolio.international
    bonds = user_portfolio.bonds
    money_market = user_portfolio.money_market

    total_investments = sum([domestic, international, bonds, money_market])

    # Calculate current percentages
    percent_domestic = domestic / total_investments
    percent_international = international / total_investments
    percent_bonds = bonds / total_investments
    percent_money_market = money_market / total_investments

    # Determine target percentages
    target_domestic_percent = selected_preset['domestic_stock']
    target_international_percent = selected_preset['international_stock']
    target_bonds_percent = selected_preset['bonds']
    target_money_market_percent = selected_preset['money_market']

    # Calculate target investments
    target_domestic_investment = target_domestic_percent * total_investments
    target_international_investment = target_international_percent * total_investments
    target_bonds_investment = target_bonds_percent * total_investments
    target_money_market_investment = target_money_market_percent * total_investments

    # Calculate rebalance $ amount
    cash_diff_domestic = target_domestic_investment - domestic
    cash_diff_international = target_international_investment - international
    cash_diff_bonds = target_bonds_investment - bonds
    cash_diff_money_market = target_money_market_investment - money_market

    # Calculate rebalance %
    percent_diff_domestic = target_domestic_percent - percent_domestic
    percent_diff_international = target_international_percent - percent_international
    percent_diff_bonds = target_bonds_percent - percent_bonds
    percent_diff_money_market = target_money_market_percent - percent_money_market

    # Pack columns
    domestic_row = ["Domestic Stock", domestic, percent_domestic, target_domestic_percent, cash_diff_domestic, percent_diff_domestic]
    international_row = ["International Stock", international, percent_international, target_international_percent, cash_diff_international, percent_diff_international]
    bonds_row = ["Bonds", bonds, percent_bonds, target_bonds_percent, cash_diff_bonds, percent_diff_bonds]
    money_market_row = ["Money Market", money_market, percent_money_market, target_money_market_percent, cash_diff_money_market, cash_diff_money_market, percent_diff_money_market]

    # Pack rows
    output = [domestic_row, international_row, bonds_row, money_market_row]

    return render_template('results.html', title='Results', data=output, preset_name=preset_name)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = forms.LoginForm()

    if request.method == "GET":
        # user already logged in, redirect to dashboard
        if "user" in session:
            flash("Already logged in!", "success")
            return redirect(url_for("userDashboard"))
        # user must login, redirected to login
        return render_template('login.html', form = form)
    
    elif request.method == "POST" and form.validate_on_submit():
        user = request.form['username']
        password = request.form['password']
        user_query = User.query.filter_by(username=user).first()

        # username not in db
        if user_query is None:
            flash("Username invalid, please register or try again", "error")
            return render_template('login.html', form = form)
        
        # password for user was incorrect
        elif user_query.password != password:
            flash("Invalid Login", "error")
            return render_template('login.html', form = form)
        
        # login successful
        else:
            session['user'] = user_query.username
            session['userID'] = user_query.id
            return redirect(url_for('userDashboard'))


@app.route('/userDashboard')
def userDashboard():
    if 'user' in session:
        user = session['user']
        return render_template('userDashboard.html', user = user)
    else:
        return NotLoggedIn()



@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('userID', None)
    flash("Logged out", "success")
    return redirect(url_for('home'))


def NotLoggedIn():
    flash("Please login or register")
    return redirect(url_for('home'))

# run on debug mode to not re-start server after changes
if __name__ == '__main__':

    app.run(debug = True)
