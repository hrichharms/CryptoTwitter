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

