import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql://nabiali:27051994@db4free.net:3306/pizzaproject'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
