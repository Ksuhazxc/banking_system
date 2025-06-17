from datetime import datetime
from extensions import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    passport = db.Column(db.String(20), unique=True, nullable=False)
    contacts = db.Column(db.String(200), nullable=False)
    accounts = db.relationship('Account', backref='client', lazy=True)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(34), unique=True, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    balance = db.Column(db.Numeric(15, 2), default=0)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Добавляем отношения:
    sender = db.relationship(
        'Account',
        foreign_keys=[sender_id],
        backref=db.backref('sent_transactions', lazy=True),
        lazy=True
    )
    receiver = db.relationship(
        'Account',
        foreign_keys=[receiver_id],
        backref=db.backref('received_transactions', lazy=True),
        lazy=True
    )