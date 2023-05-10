from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, request , session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField , IntegerField
from wtforms.validators import DataRequired, Length , EqualTo , NumberRange
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    login_required
from jinja2 import environment
import os
import sqlite3 as db


app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.urandom(65)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 16)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 20)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#@app.route('/register')
    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.username)

class register_form(FlaskForm):
    username = StringField(label="Username" , validators=[DataRequired(),Length(min =3, max=20)])
    password = PasswordField(label="Password" ,validators=[DataRequired(),Length(min=6 , max=20)])
    confirm_password=PasswordField(label="Confirm Password" ,validators=[DataRequired(), EqualTo('password')])
    Submit =SubmitField(label="Sign up")

class checkout_form(FlaskForm):
    Card_num = IntegerField(label = "Card_num" , validators=[DataRequired(), NumberRange(min =1 , max = 9999999999999999)])
    Security_numb = IntegerField(label ="Security_num",validators=[DataRequired(), NumberRange(min =1 ,max = 999)])
    EXP_date_mon = IntegerField(label = "EXP_date_mon",validators=[DataRequired() , NumberRange(min = 1 , max = 12) ])
    EXP_date_Year = IntegerField(label = "EXP_date_Year",validators=[DataRequired() , NumberRange(min=2020 , max = 2123)] )
    Address = StringField(IntegerField(label = "Address",validators=[DataRequired(),Length(8 , 30)]))

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.Text(), nullable = False)
    engine = db.Column(db.String(50) , nullable = False)
    torque = db.Column(db.String(50) , nullable = False)
    transmission = db.Column(db.String(50) , nullable = False)
    weight = db.Column(db.String(50) , nullable = False)
    size = db.Column(db.String(50) , nullable = False)
    zero_to_60 = db.Column(db.String(50) , nullable = False)
    price = db.Column(db.Float(), nullable = False)
    e_impact = db.Column(db.String(50) , nullable = False)
    image_url = db.Column(db.String(64), nullable = False)



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


#@app.route("/login" , methods=["POST","GET"])
#def login():
#    form = LoginForm()
    #username = request.form('username')
    #password = request.form('password')
    #User.username = username
    #User.password_hash = password
#    if form.validate_on_submit():
#        return redirect(url_for('index'))
#    return render_template('login.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('login', **request.args))
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register' ,methods=["POST","GET"] )
def register_user():
    form=register_form()
    if form.validate_on_submit():
        User.register(form.username.data , form.password.data)
        return redirect(url_for('login'))
    return render_template("register.html",form=form) 

@app.route('/', methods=["POST" , "GET"])
def index():
    items = Products.query.all()
    products = {}
    for item in items:
        name = item.name
        products[name] = {}
        products [name]["price"] = item.price
        products [name]["e_impact"] = item.e_impact
        products [name]["img"] = item.image_url

    if(request.method == "POST" and "name" in request.form):
        if(request.form["name"] != None):
            item_name = request.form["name"]
            #added_product = Products.query.filter_by(name=item_name).first()
            Basket_adding(item_name)
    
        
    return render_template('index.html', products=products)

def Basket_adding(name):
    if("basket" not in session):
        session["basket"] = []
        session["basket"].append(name)
    else:
        session["basket"].append(name)
        session.modified = True

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500



@app.route('/Basket', methods=["POST" , "GET"])
def Basket():
    items = {}
    if(request.method == "POST" and "clear_all" in request.form):
        session.pop("basket")
        session.modified = True
    if(request.method == "POST" and "Clear_item" in request.form):
        session["basket"] = [name for name in session["basket"] if name !=  request.form["Clear_item"]]
        session.modified = True
    if(request.method == "POST" and "Checkout" in request.form):
        return Checkout()
    if ("basket" in session):
        for name in session["basket"]:
            added_product = Products.query.filter_by(name=name).first()
            
            if (name in items):
                print(items[name]["amount"])
                items[name]["amount"] += 1
            else:
                items[name] = {"price": added_product.price, "amount": 1}
    return render_template("Basket.html" ,items=items )

@app.route('/Product' , methods=['POST' , 'GET'])
def Product_page():
    Car_name = request.args.get("Car_name")  
    if (Car_name == None): # if users chooses a page with no car it then goes to the index function which goes to the product page
        return index()
    
    if(request.method == "POST" and "name" in request.form):
        if(request.form["name"] != None):
            item_name = request.form["name"]
            Basket_adding(item_name)
    
    # looks through the database 
    searched_car = Products.query.filter_by(name=Car_name).first()
    if(searched_car == None):
        return index()
    else:
        return render_template("Product.html" , name=Car_name , description = searched_car.description , Engine =searched_car.engine ,Torque = searched_car.torque,Transmission = searched_car.transmission ,Weight = searched_car.weight, Size = searched_car.size, Zero_to_60 = searched_car.zero_to_60, Price =searched_car.price , E_impact = searched_car.e_impact , Image =searched_car.image_url)

@app.route('/Checkout', methods=['GET', 'POST'])
def Checkout():
    form = checkout_form()
    Error =""
    Error_2 = ""
    Error_3 = ""
    Error_4 = ""
    if form.validate_on_submit():
        card_num = str(request.form["Card_num"])
        Security_num = str(request.form["Security_numb"])
        EXP_date_mon = str(request.form["EXP_date_mon"])
        EXP_date_Year = str(request.form["EXP_date_Year"])
        if (len(card_num) <16):
            Error =("Please enter a valid card number")
            return render_template("Checkout.html" , form=form, error=Error , error_2=Error_2 , error_3=Error_3,error_4 = Error_4) 
        if (len(Security_num) < 3):
            Error_2=("Enter a valid Security number")
            return render_template("Checkout.html" , form=form, error=Error , error_2=Error_2 , error_3=Error_3,error_4 = Error_4) 
        if(len(EXP_date_mon) < 2):
            Error_3=("Enter a valid expiry month")
            return render_template("Checkout.html" , form=form, error=Error , error_2=Error_2 , error_3=Error_3,error_4 = Error_4) 
        if(len(EXP_date_Year) < 4):
            Error_4 =("Enter a valid expiry year")
            return render_template("Checkout.html" , form=form, error=Error , error_2=Error_2 , error_3=Error_3,error_4 = Error_4) 
        
        session.pop('basket')
        session.modified = True
        return render_template("Payment.html")
        
    return render_template("Checkout.html" , form=form, error=Error , error_2=Error_2 , error_3=Error_3,error_4 = Error_4) 
    
@app.route('/Payment')
def Payment():
    return render_template("Payment.html")

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
