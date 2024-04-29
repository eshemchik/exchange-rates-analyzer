#!/usr/bin/env python3

import requests
from flask import Flask, request,redirect

app = Flask(__name__)

BASE_CURRENCIES_ALLOWLIST = [
    'usd',
    'eur',
    'gbp',
    'chf',
    'btc',
]

BACKEND_PATH = 'http://127.0.0.1:5001/'


@app.route("/")
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


@app.route("/get_results", methods=["GET"])
def get_results():
    analysis_id = request.args.get("analysis_id", "")
    response = requests.get(f"{BACKEND_PATH}get_results?analysis_id={analysis_id}")
    rows = ""
    for r in response.json()['rows']:
        if r['currency'] == r['base_currency']:
            continue
        rows += f"<tr><td>{r['currency']}/{r['base_currency']}</td><td>{r['rate_change_percents']}</td></tr>"
    return f'''
    <table>
    <tr><th>Currencies pair</th><th>Change(%)</th></tr>
    {rows}
    </table>
    '''


if __name__ == '__main__':
    app.run(port=5000)