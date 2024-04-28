#!/usr/bin/env python3

import requests
import sys
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
sys.path.append('../../components')
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Rates.sqlite3'

db = SQLAlchemy(app)


def get_rates(base_currency, date):
    app.logger.info(f"Requesting data for '{base_currency}' for date '{date}'")
    response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
    app.logger.info("Got response: " + str(response))
    return response.json()[base_currency]


@app.route("/initiate_analysis", methods=["POST"])
def initiate_analysis():
    base_currency = request.form.get("base_currency", "")
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    analysis_id = str(hash(base_currency + "#" + start_date + "#" + end_date))

    rates_from = get_rates(base_currency, start_date)
    rates_to = get_rates(base_currency, end_date)
    diff = dict()
    for k, v in rates_from.items():
        if k in COMPARABLE_CURRENCIES_ALLOWLIST:
            diff[k] = (rates_to[k] / rates_from[k] - 1) * 100.

    with app.app_context():
        init_db(db)
        for k, v in diff.items():
            existing = db.session.query(AnalysisResults).filter_by(
                id=analysis_id, currency=k, base_currency=base_currency, rate_change_percents=v
            ).first()
            if existing:
                continue
            entry = AnalysisResults(id=analysis_id, currency=k, base_currency=base_currency, rate_change_percents=v)
            db.session.add(entry)
        db.session.commit()
    return '{"analysis_id":"' + analysis_id + '"}'


class ResultRow:
    def __init__(self, base_currency, currency, rate_change_percents):
        self.base_currency = base_currency
        self.currency = currency
        self.rate_change_percents = rate_change_percents

    def json(self):
        return '{"base_currency":"'+self.base_currency+'",currency:"'+self.currency+'",rate_change_percents:"'+str(self.rate_change_percents)+'"}'


@app.route("/get_results", methods=["GET"])
def get_results():
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
    return '[' + ','.join(resps) + ']'


if __name__ == '__main__':
    app.run(port=5001, debug=True)