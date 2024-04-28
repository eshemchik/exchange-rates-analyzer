#!/usr/bin/env python3

from flask import Flask, request

app = Flask(__name__)

BASE_CURRENCIES_ALLOWLIST = [
    'usd',
    'eur',
    'gbp',
    'chf',
    'btc',
]

BACKEND_PATH = 'http://localhost:8081'


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

    return "You entered: " + base_currency + " " + start_date + " " + end_date