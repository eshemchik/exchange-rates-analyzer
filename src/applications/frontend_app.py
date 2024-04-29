#!/usr/bin/env python3

import requests
from flask import Flask, request,redirect
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app, group_by='endpoint')

common_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

BASE_CURRENCIES_ALLOWLIST = [
    'usd',
    'eur',
    'gbp',
    'chf',
    'btc',
]

BACKEND_PATH = 'http://127.0.0.1:5001/'


@app.route("/")
@common_counter
def main():
    options = ""
    for cur in BASE_CURRENCIES_ALLOWLIST:
        options += f"<option value='{cur}'>{cur}</option>"
    return f'''
     <form action="/initiate_analysis" method="POST">
         Select base currency: 
         <select name="base_currency">
            {options}
         </select>
         <br>
         Select start date (e.g. 2024-04-01) <input name="start_date"><br>
         Select end date (e.g. 2024-04-25) <input name="end_date"><br>
         <input type="submit" value="Analyze!">
     </form>
     '''


@app.route("/initiate_analysis", methods=["POST"])
@common_counter
def initiate_analysis():
    base_currency = request.form.get("base_currency", "")
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    response = requests.post(BACKEND_PATH + "initiate_analysis", data={
        "base_currency": base_currency,
        "start_date": start_date,
        "end_date": end_date,
    })
    analysis_id = response.json()['analysis_id']
    return redirect(f"/get_results?analysis_id={analysis_id}", code=302)


def render_results(backend_response):
    rows = ""
    start_date = backend_response['rows'][0]['start_date']
    end_date = backend_response['rows'][0]['end_date']
    for r in backend_response['rows']:
        if r['currency'] == r['base_currency']:
            continue
        rows += f"<tr><td>{r['currency']}/{r['base_currency']}</td><td>{r['start_rate']}</td><td>{r['end_rate']}</td><td>{r['rate_change_percents']}</td></tr>"
    return f'''
    If no results shown, please refresh the page in a couple of seconds.
    <table>
    <tr><th>Currencies pair</th><th>{start_date}</th><th>{end_date}</th><th>Change(%)</th></tr>
    {rows}
    </table>
    '''


@app.route("/get_results", methods=["GET"])
@common_counter
def get_results():
    analysis_id = request.args.get("analysis_id", "")
    response = requests.get(f"{BACKEND_PATH}get_results?analysis_id={analysis_id}")
    return render_results(response.json())


@app.route("/health")
@common_counter
def health():
    return "i'm healthy"


if __name__ == '__main__':
    app.run(port=5000)