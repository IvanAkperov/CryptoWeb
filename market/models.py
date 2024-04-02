from datetime import datetime

from market import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    increase = db.Column(db.String(20), nullable=False, default="0%")
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Currency {self.name}"


class UserCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    quantity = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('currencies', lazy=True))
    currency = db.relationship('Currency', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f"UserCurrency {self.user_id} - {self.currency_id}"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hashed = db.Column(db.String(60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    last_spin = db.Column(db.DateTime, default=datetime.utcnow)

    def buy_currency(self, currency, quantity):
        if self.budget < currency.price * quantity:
            raise ValueError("Not enough budget")
        if currency.quantity < quantity:
            raise ValueError("Not enough currency in stock")

        user_currency = UserCurrency.query.filter_by(user_id=self.id, currency_id=currency.id).first()
        if user_currency:
            user_currency.quantity += quantity
        else:
            user_currency = UserCurrency(user_id=self.id, currency_id=currency.id, quantity=quantity)
            db.session.add(user_currency)

        self.budget -= currency.price * quantity
        currency.quantity -= quantity
        db.session.commit()

    def sell_currency(self, currency, quantity):
        user_currency = UserCurrency.query.filter_by(user_id=self.id, currency_id=currency.id).first()
        if user_currency:
            user_currency.quantity -= quantity

        self.budget += currency.price * quantity
        currency.quantity += quantity
        db.session.commit()

    def spin_the_wheel(self, amount):
        user = User.query.filter_by(id=self.id)
        if user:
            self.budget += amount
            db.session.commit()
