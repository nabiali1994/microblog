from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)   

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) 

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.String(1040))
    price = db.Column(db.Float)

    def __repr__(self):
        return '<Pizza {}>'.format(self.id)
        
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Order {}>'.format(self.id)

class Pizza_ordered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_id = db.Column(db.Integer, db.ForeignKey('command.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Pizza_ordered {}>'.format(self.id)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'))
    pizza_title = db.Column(db.String(140))
    pizza_price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Cart_ordered {}>'.format(self.id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))