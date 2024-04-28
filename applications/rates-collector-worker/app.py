#!/usr/bin/env python3


import requests
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
sys.path.append('../../components')
from components.rates_db import Rates
from components.rates_db import init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Rates.sqlite3'

db = SQLAlchemy(app)


def get_rates(base_currency, date):
    response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
    return response.json()[base_currency]


if __name__ == "__main__":
    with app.app_context():
        init_db(db)
        rates = get_rates('eur', '2024-03-07')
        for k, v in rates.items():
            entry = Rates(base_currency='eur', date='2024-03-07', currency=k, rate=v)
            existing = db.session.query(Rates).filter_by(base_currency='eur', date='2024-03-07', currency=k).first()
            if not existing:
                db.session.add(entry)
        db.session.commit()