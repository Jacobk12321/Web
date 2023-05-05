from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, request , session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    login_required
import re
import os


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
    password = PasswordField('Password', validators=[DataRequired()])
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

    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.username)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    e_impact = db.Column(db.String(50) , nullable=False)



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate():
        user = User.query.filer(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('login.html', **request.args))
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index.html'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.html'))


@app.route('/', methods=["POST" , "GET"])
def index():
    if(request.method == "POST" and "name" in request.form):
        if(request.form["name"] != None):
            item_name = request.form["name"]
            #added_product = Products.query.filter_by(name=item_name).first()
            Basket_adding(item_name)

        
    return render_template('index.html')

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
    if ("basket" in session):
        for name in session["basket"]:
            added_product = Products.query.filter_by(name=name).first()
            
            if (name in items):
                print(items[name]["amount"])
                items[name]["amount"] += 1
            else:
                items[name] = {"price": added_product.price, "amount": 1}
    return render_template("Basket.html" ,items=items )


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
