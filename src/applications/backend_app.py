#!/usr/bin/env python3

import requests
import json
import pika
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from components.rates_db import RatesDAO
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Rates.sqlite3'

db = SQLAlchemy(app)

metrics = PrometheusMetrics(app, group_by='endpoint')

common_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)


@app.route("/initiate_analysis", methods=["POST"])
@common_counter
def initiate_analysis():
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
    def __init__(self, base_currency, currency, start_date, end_date, start_rate, end_rate, rate_change_percents):
        self.base_currency = base_currency
        self.currency = currency
        self.start_date = start_date
        self.end_date = end_date
        self.start_rate = start_rate
        self.end_rate = end_rate
        self.rate_change_percents = rate_change_percents

    def json(self):
        return ('{"base_currency":"'+self.base_currency
                +'","currency":"'+self.currency
                +'","start_date":"'+self.start_date
                +'","end_date":"'+self.end_date
                +'","start_rate":"'+str(self.start_rate)
                +'","end_rate":"'+str(self.end_rate)
                +'","rate_change_percents":"'+str(self.rate_change_percents)+'"}')


def get_results_impl(dao, analysis_id):
    if analysis_id == "":
        raise RuntimeError("no analysis id provided")
    results = dao.read_analysis_results(analysis_id)
    result_rows = []
    for r in results:
        result_rows.append(ResultRow(
            r.base_currency, r.currency, r.start_date, r.end_date, r.start_rate, r.end_rate, r.rate_change_percents
        ))
    result_rows.sort(key=lambda x: x.rate_change_percents)
    resps = []
    for r in result_rows:
        resps.append(r.json())
    return '{"rows":[' + ','.join(resps) + ']}'


@app.route("/get_results", methods=["GET"])
@common_counter
def get_results():
    return get_results_impl(dao=RatesDAO(db), analysis_id=request.args.get("analysis_id", ""))


@app.route("/health")
@common_counter
def health():
    return "i'm healthy"


if __name__ == '__main__':
    app.run(port=5001)