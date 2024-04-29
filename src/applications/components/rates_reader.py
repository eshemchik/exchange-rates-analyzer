import requests

class RatesReader:
    def __init__(self):
        pass

    def get_rates(self, base_currency, date):
        response = requests.get(f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base_currency}.json")
        return response.json()[base_currency]
