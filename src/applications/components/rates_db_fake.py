class FakeRatesDAO:
    def __init__(self):
        self.rates = []
        self.results = []

    def read_analysis_results(self, analysis_id):
        return list(filter(lambda x: x.id == analysis_id, self.results))

    def read_rates(self, base_currency, date):
        return list(filter(lambda x: x.base_currency == base_currency and x.date == date, self.rates))

    def write_analysis_results(self, entries):
        self.results.extend(entries)

    def write_rates(self, entries):
        self.rates.extend(entries)
