#!/usr/bin/env python3

import unittest

from frontend_app import render_results


class TestFrontend(unittest.TestCase):
    def test_render_results(self):
        backend_response = dict({
            "rows": [{
                "base_currency": "usd",
                "currency": "eur",
                "start_date": "2024-04-01",
                "end_date": "2024-04-02",
                "start_rate": "1.0",
                "end_rate": "1.1",
                "rate_change_percents": "10",
            }]
        })
        got_rendered = render_results(backend_response)
        want_rendered = '''
    If no results shown, please refresh the page in a couple of seconds.
    <table>
    <tr><th>Currencies pair</th><th>2024-04-01</th><th>2024-04-02</th><th>Change(%)</th></tr>
    <tr><td>eur/usd</td><td>1.0</td><td>1.1</td><td>10</td></tr>
    </table>
    '''
        self.assertEquals(want_rendered, got_rendered, "Returned wrong rendered page")


if __name__ == '__main__':
    unittest.main()