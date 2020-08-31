from app import app
from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_role = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format((self.username))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    category = db.Column(db.ForeignKey('category.id'))
    avaliable = db.Column(db.Boolean) 
    price = db.Column(db.DECIMAL(7, 2))
    image = db.Column(db.String(128))
    description = db.Column(db.String(1024))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), index=True)
    parents = db.Column(db.ForeignKey('category.id'))
    description = db.Column(db.String(1024))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fname = db.Column(db.String)
    lname = db.Column(db.String)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    payment = db.Column(db.String)
    totalprice = db.Column(db.DECIMAL(7, 2))
    finished = db.Column(db.Integer, default=0)


class Order_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    good_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    count = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
