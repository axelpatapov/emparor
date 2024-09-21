from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

#Define the models (database structure).

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    media = db.Column(db.String(100), nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())

    sender = db.relationship('User', foreign_keys=[sender_id])

#måste också göra en klass Video Message
#möjligtvis en klass interakt, där användare kan interagera med profilernas uppgifter, som att 
#få en nyckel för att öppna en bild