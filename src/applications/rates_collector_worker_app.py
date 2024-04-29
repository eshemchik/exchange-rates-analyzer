#!/usr/bin/env python3


import sys
import pika
import os
import json
import traceback

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from components.rates_db import RatesDAO, Rates
from components.rates_reader import RatesReader

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


def request_and_store_data(dao, rates_reader, base_currency, date):
    rates = rates_reader.get_rates(base_currency, date)
    entries = []
    for k, v in rates.items():
        if k not in COMPARABLE_CURRENCIES_ALLOWLIST:
            continue
        entries.append(Rates(base_currency=base_currency, date=date, currency=k, rate=1/v))
    dao.write_rates(entries)


def process_request(request, dao, rates_reader):
    print("Processing collecting request: " + str(request))
    request_and_store_data(dao, rates_reader, request['base_currency'], request['start_date'])
    request_and_store_data(dao, rates_reader, request['base_currency'], request['end_date'])
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = conn.channel()
    channel.exchange_declare(exchange="analyze-requests-exchange",exchange_type="direct")
    channel.queue_declare(queue="analyze-requests")
    channel.basic_publish(exchange="analyze-requests-exchange", routing_key="analyze-requests",
                          body=json.dumps({
                              "base_currency": request['base_currency'],
                              "start_date": request['start_date'],
                              "end_date": request['end_date'],
                              "analysis_id": request['analysis_id'],
                              }))
    print("Processed collecting request: " + str(request))


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange="incoming-requests-exchange",exchange_type="direct")
    channel.queue_declare(queue="incoming-requests")
    channel.queue_bind(exchange="incoming-requests-exchange", queue="incoming-requests", routing_key="incoming-requests")
    def callback(ch, method, properties, body):
        try:
            body = json.loads(body)
            with app.app_context():
                process_request(body, RatesDAO(db), RatesReader())
        except Exception:
            traceback.print_exc()
    channel.basic_consume(queue='incoming-requests', on_message_callback=callback, auto_ack=True)
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