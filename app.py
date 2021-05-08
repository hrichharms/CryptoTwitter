from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from datetime import datetime
import json


# Flask app and database initialization
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    balance = db.Column(db.Float)

    def __init__(self, email, password):
        self.id = id
        self.email = email
        self.password = password
        self.balance = 0.0


class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(db.Integer, primary_key=True)
    crypto_symbol = db.Column(db.String)
    amount = db.Column(db.Float)
    hold_days = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, crypto_symbol, amount, hold_days, user_id):
        self.crypto_symbol = crypto_symbol
        self.amount = amount
        self.hold_days = hold_days
        self.user_id = user_id


class ListenerAccount(db.Model):
    __tablename__ = "listener_accounts"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String)
    listener_id = db.Column(db.Integer, db.ForeignKey("listeners.id"))

    def __init__(self, account, listener_id):
        self.account = account
        self.listener_id = listener_id



@app.route("/users/auth")
def authenticate():
    return {"success": 1}


@app.route("/users")
def get_users():
    users = User.query.all()
    return {"users": [dict(id=user.id, email=user.email, password=user.password) for user in users]}


@app.route("/users/<user_id>")
def get_user(user_id):
    user = User.get_or_404(user_id)
    return {"id": user.id, "email": user.email, "password": user.password}


@app.route("/users", methods=["POST"])
def new_user():
    user = User(request.json["email"], request.json["password"])
    db.session.add(user)
    db.session.commit()
    return {"id": user.id}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
