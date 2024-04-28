#!/usr/bin/env python3


import requests
import sys
import pika
import os
import json
import traceback

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
sys.path.append('../../components')
from components.rates_db import Rates
from components.rates_db import AnalysisResults
from components.rates_db import init_db


COMPARABLE_CURRENCIES_ALLOWLIST = [
    'usd',
    'eur',
    'gbp',
    'chf',
    'btc',
]


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Rates.sqlite3'

db = SQLAlchemy(app)


def get_rates(base_currency, date):
    response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
    return response.json()[base_currency]


def request_and_store_data(base_currency, date):
    rates = get_rates(base_currency, date)
    for k, v in rates.items():
        if k not in COMPARABLE_CURRENCIES_ALLOWLIST:
            continue
        existing = db.session.query(Rates).filter_by(
            base_currency=base_currency, date=date, currency=k
        ).first()
        if existing:
            continue
        entry = Rates(base_currency=base_currency, date=date, currency=k, rate=v)
        db.session.add(entry)
    db.session.commit()


def process_request(request):
    print("Processing request: " + str(request))
    with app.app_context():
        init_db(db)
        start_rates_entries = db.session.query(Rates).filter_by(
            base_currency=request['base_currency'], date=request['start_date']
        )
        end_rates_entries = db.session.query(Rates).filter_by(
            base_currency=request['base_currency'], date=request['end_date']
        )
        rates_from = dict()
        for entry in start_rates_entries:
            rates_from[entry.currency] = entry.rate
        rates_to = dict()
        for entry in end_rates_entries:
            rates_to[entry.currency] = entry.rate
        diff = dict()
        for k, v in rates_from.items():
            if k in COMPARABLE_CURRENCIES_ALLOWLIST:
                diff[k] = (rates_to[k] / rates_from[k] - 1) * 100.
        with app.app_context():
            init_db(db)
            for k, v in diff.items():
                existing = db.session.query(AnalysisResults).filter_by(
                    id=request['analysis_id'], currency=k, base_currency=request['base_currency'], rate_change_percents=v
                ).first()
                if existing:
                    continue
                entry = AnalysisResults(id=request['analysis_id'], currency=k, base_currency=request['base_currency'], rate_change_percents=v)
                db.session.add(entry)
            db.session.commit()


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange="analyze-requests-exchange",exchange_type="direct")
    channel.queue_declare(queue="analyze-requests")
    channel.queue_bind(exchange="analyze-requests-exchange", queue="analyze-requests", routing_key="analyze-requests")
    def callback(ch, method, properties, body):
        try:
            body = json.loads(body)
            process_request(body)
        except Exception as e:
            traceback.print_exc()
    channel.basic_consume(queue='analyze-requests', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)