#!/usr/bin/env python3

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Rates.sqlite3'

db = SQLAlchemy(app)


class Rates(db.Model):
    base_currency = db.Column("base_currency", db.String(20), primary_key=True)
    date = db.Column("date", db.String(20), primary_key=True)
    currency = db.Column("currency", db.String(20), primary_key=True)
    rate = db.Column("rate", db.Float)


def get_rates(base_currency, date):
    response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
    return response.json()[base_currency]


if __name__ == "__main__":
    with app.app_context():
        # Create table if not exists.
        Rates.__table__.create(bind=db.engine, checkfirst=True)

        rates = get_rates('eur', '2024-03-06')
        for k, v in rates.items():
            entry = Rates(base_currency='eur', date='2024-03-06', currency=k, rate=v)
            db.session.add(entry)
        db.session.commit()