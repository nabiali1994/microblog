from app import app
from app.forms import LoginForm, OrderForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Pizza, Cart, Pizza_ordered, Command
from app.forms import RegistrationForm
from app import db
from werkzeug.urls import url_parse
import datetime
from sqlalchemy import DateTime
import json


@app.route('/')
@app.route('/index')
def index():
    pizza = Pizza.query.all()
    return render_template("index.html", title='Home Page', pizza=pizza)

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
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    commands = Command.query.filter_by(user_id=user.id).all()
    return render_template('user.html', commands=commands)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        somme = 0
        for pizza in cart:
            somme = somme + pizza.pizza_price*pizza.quantity
        price1 = float("{:.2f}".format((somme+5)*1.12))
        return render_template('cart.html',cart=cart, price=somme+5, price1=price1)
    else:
        return render_template('cart.html')


@app.route('/fin', methods=['GET', 'POST'])
def finish():
    form = OrderForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            cart = Cart.query.filter_by(user_id=current_user.id).all()
            command = Command(user_id=current_user.id)
            db.session.add(command)
            db.session.flush() 
            for pizza in cart:
                pizza_ordered = Pizza_ordered(command_id= command.id, pizza_id= pizza.pizza_id, quantity= pizza.quantity)
                db.session.add(pizza_ordered)
            db.session.commit()
            return redirect(url_for('order'))
    if form.validate_on_submit():
        return redirect(url_for('order'))
    return render_template('fin.html', form=form, user=current_user)


@app.route('/order')
def order():
    if current_user.is_authenticated:
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    return render_template('endorder.html')

    
@app.route('/getpizza/<id>')
def getpizza(id):
    pizza = Pizza.query.filter_by(id=id).first()
    return '{"title": "'+pizza.title+'", "description":"'+pizza.description+'", "price": '+str(pizza.price)+'}'

@app.route('/getcardpizzas')
def getcardpizzas():
    if current_user.is_authenticated:
        cart =Cart.query.filter_by(user_id=current_user.id)
        somme = 0
        for pizza in cart:
            somme = somme + pizza.quantity
        return str(somme)
    return 'nothing'

@app.route('/clearall/<user_id>')
def clearall(user_id):
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return 'done'

@app.route('/clearitem/<item_id>')
def clearitem(item_id):
    Cart.query.filter_by(id=item_id).delete()
    db.session.commit()
    return 'done'

@app.route('/getorderpizzas/<order_id>')
def getorderpizzas(order_id):
    pizzas = Pizza_ordered.query.filter_by(command_id=order_id)
    l = []
    i=0
    for prod in pizzas:
        current_pizza = Pizza.query.filter_by(id=prod.pizza_id).first_or_404()
        print (current_pizza.title)
        print (prod.quantity)
        x = {"item":{"title":current_pizza.title,"quantity":prod.quantity}}
        l.append(x)
        i=i+1
    return json.dumps(l)

    

@app.route('/savetocart/<user_id>/<pizza_id>')
def savetocart(user_id, pizza_id):
    print('here')
    pizza = Pizza.query.filter_by(id=pizza_id).first()
    cart_toupdate =Cart.query.filter_by(user_id=user_id, pizza_id=pizza_id).first()
    if cart_toupdate is None:
        cart = Cart(user_id=user_id, pizza_id=pizza_id, quantity=1, pizza_title=pizza.title, pizza_price=pizza.price)
        db.session.add(cart)
        db.session.commit()
    else:
        cart_toupdate.quantity += 1 
        db.session.commit()
    return 'done'
    