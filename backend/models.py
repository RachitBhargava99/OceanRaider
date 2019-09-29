from backend import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(127), nullable=False)
    email = db.Column(db.String(63), unique=True, nullable=False)
    password = db.Column(db.String(63), unique=False, nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)

    def get_auth_token(self, expires_seconds=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User ID {self.id}"


@login_manager.user_loader
def load_user(user_id):
    return LoggedInUser.query.get(int(user_id))


class LoggedInUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(127))
    email = db.Column(db.String(127))
    auth_token = db.Column(db.String(255))

    def __init__(self, id, name, email, auth_token):
        self.user_id = id
        self.name = name
        self.email = email
        self.auth_token = auth_token

class Port(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port_id = db.Column(db.Integer, unique=False, nullable=False)
    cargo = db.Column(db.Integer, unique=False, default=0)
    food = db.Column(db.Integer, unique=False, default=0)
    coor_x = db.Column(db.Integer, default=0)
    coor_y = db.Column(db.Integer, default=0)
    is_dest = db.Column(db.Boolean, unique=False, default=False)
    x_coord = db.Column(db.Integer, unique=False, default=False)
    y_coord = db.Column(db.Integer, unique=False, default=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)


class Ship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ship_id = db.Column(db.Integer, default=0)
    life_points = db.Column(db.Integer, unique=False, default=10)
    cargo = db.Column(db.Integer, unique=False, default=0)
    cannon = db.Column(db.Integer, unique=False, default=1)
    crew = db.Column(db.Integer, unique=False, default=1)
    food = db.Column(db.Integer, unique=False, default=0)
    speed = db.Column(db.Integer, unique=False, default=1)
    is_bot = db.Column(db.Boolean, unique=False, default=False)
    home_port = db.Column(db.Integer, db.ForeignKey('port.port_id'), unique=False, default=0)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
