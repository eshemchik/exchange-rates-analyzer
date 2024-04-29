class FakeRatesReader:
    def __init__(self):
        pass
    def get_rates(self, base_currency, date):
        return dict({
            "eur": 1.1
        })
