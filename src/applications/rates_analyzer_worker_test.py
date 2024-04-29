#!/usr/bin/env python3

import unittest

from components.rates_db_fake import FakeRatesDAO
from components.rates_db import Rates, AnalysisResults
from rates_analyzer_worker_app import process_request


class TestRatesAnalyzer(unittest.TestCase):
    def test_analyze(self):
        rates = [
            Rates(base_currency="usd", date="2024-04-01", currency="eur", rate=1.1),
            Rates(base_currency="usd", date="2024-04-02", currency="eur", rate=1.2),
        ]
        dao = FakeRatesDAO()
        dao.write_rates(rates)
        req = dict({
              "base_currency": "usd",
              "start_date": "2024-04-01",
              "end_date": "2024-04-02",
              "analysis_id": "1",
        })
        process_request(req, dao)
        got_results = dao.read_analysis_results(analysis_id="1")
        self.assertEquals(len(got_results), 1, "Returned results count is wrong")


if __name__ == '__main__':
    unittest.main()