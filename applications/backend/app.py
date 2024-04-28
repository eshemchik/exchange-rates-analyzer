#!/usr/bin/env python3

import requests
import sys
import json
import pika
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
sys.path.append('../../components')
from components.rates_db import AnalysisResults
from components.rates_db import init_db



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Rates.sqlite3'

db = SQLAlchemy(app)


def get_rates(base_currency, date):
    app.logger.info(f"Requesting data for '{base_currency}' for date '{date}'")
    response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
    app.logger.info("Got response: " + str(response))
    return response.json()[base_currency]


@app.route("/initiate_analysis", methods=["POST"])
def initiate_analysis():
    init_db(db)
    base_currency = request.form.get("base_currency", "")
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    analysis_id = str(hash(base_currency + "#" + start_date + "#" + end_date))

    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = conn.channel()
    channel.exchange_declare(exchange="incoming-requests-exchange",exchange_type="direct")
    channel.queue_declare(queue="incoming-requests")
    channel.basic_publish(exchange="incoming-requests-exchange", routing_key="incoming-requests",
                          body=json.dumps({
                              "base_currency": base_currency,
                              "start_date": start_date,
                              "end_date": end_date,
                              "analysis_id": analysis_id,
                          }))

    return '{"analysis_id":"' + analysis_id + '"}'


class ResultRow:
    def __init__(self, base_currency, currency, rate_change_percents):
        self.base_currency = base_currency
        self.currency = currency
        self.rate_change_percents = rate_change_percents

    def json(self):
        return '{"base_currency":"'+self.base_currency+'","currency":"'+self.currency+'","rate_change_percents":"'+str(self.rate_change_percents)+'"}'


@app.route("/get_results", methods=["GET"])
def get_results():
    init_db(db)
    analysis_id = request.args.get("analysis_id", "")
    if analysis_id == "":
        raise RuntimeError("no analysis id provided")
    results = db.session.query(AnalysisResults).filter_by(id=analysis_id)
    result_rows = []
    for r in results:
        result_rows.append(ResultRow(r.base_currency, r.currency, r.rate_change_percents))
    result_rows.sort(key=lambda x: x.rate_change_percents)
    resps = []
    for r in result_rows:
        resps.append(r.json())
    return '{"rows":[' + ','.join(resps) + ']}'


if __name__ == '__main__':
    app.run(port=5001)