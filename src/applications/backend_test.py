#!/usr/bin/env python3

import unittest

from backend_app import get_results_impl
from components.rates_db import AnalysisResults
from components.rates_db_fake import FakeRatesDAO


class TestBackend(unittest.TestCase):
    def test_get_results(self):
        results = [
            AnalysisResults(
                id="1",
                currency="eur",
                base_currency="usd",
                start_date="2024-04-01",
                end_date="2024-04-02",
                start_rate=1.0,
                end_rate=1.1,
                rate_change_percents = 10.
            )
        ]
        dao = FakeRatesDAO()
        dao.write_analysis_results(results)
        results_json = get_results_impl(dao, analysis_id="1")
        want_json = '{"rows":[{"base_currency":"usd","currency":"eur","start_date":"2024-04-01","end_date":"2024-04-02","start_rate":"1.0","end_rate":"1.1","rate_change_percents":"10.0"}]}'
        self.assertEquals(want_json, results_json, "Returned wrong json")


if __name__ == '__main__':
    unittest.main()