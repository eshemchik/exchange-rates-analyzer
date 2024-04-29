#!/usr/bin/env python3

import unittest

from components.rates_db_fake import FakeRatesDAO
from components.rates_reader_fake import FakeRatesReader
from components.rates_db import Rates
from rates_collector_worker_app import process_request


class TestRatesCollector(unittest.TestCase):
    def test_collect(self):
        rates = [Rates(base_currency="usd", date="2024-04-01", currency="eur", rate=1.1)]
        dao = FakeRatesDAO()
        rates_reader = FakeRatesReader()
        req = dict({
              "base_currency": "usd",
              "start_date": "2024-04-01",
              "end_date": "2024-04-02",
              "analysis_id": "1",
        })
        process_request(req, dao, rates_reader)
        got_rates = dao.read_rates(base_currency="usd", date="2024-04-01")
        self.assertEquals(len(rates), len(got_rates), "Returned rates count is wrong")


if __name__ == '__main__':
    unittest.main()