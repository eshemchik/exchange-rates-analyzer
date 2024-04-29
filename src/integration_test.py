#!/usr/bin/env python3

import requests
import time
import re
from subprocess import Popen

if __name__ == '__main__':
    # rabbitmq = Popen('docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management')
    frontend = Popen('./applications/frontend_app.py')
    backend = Popen('./applications/backend_app.py')
    rates_collector = Popen('./applications/rates_collector_worker_app.py')
    rates_analyzer = Popen('./applications/rates_analyzer_worker_app.py')

    # Wait for all services to start.
    time.sleep(5)

    initiate_response = requests.post("http://127.0.0.1:5000/initiate_analysis", allow_redirects=False, data={
        "base_currency": "usd",
        "start_date": "2024-04-01",
        "end_date": "2024-04-25",
    })
    assert (initiate_response.status_code == 302, "/initiate_analysis should return redirect on results page")
    analysis_id = re.findall("[0-9\-]+", initiate_response.text)[2]

    # Wait for analysis processing.
    time.sleep(5)

    results_response = requests.get("http://127.0.0.1:5000/get_results?analysis_id=" + analysis_id)
    assert (results_response.status_code == 200, "/get_results should return 200")

    want_response = '''
    <table>
    <tr><th>Currencies pair</th><th>Change(%)</th></tr>
    <tr><td>eur/usd</td><td>0.8882877144568813</td></tr><tr><td>gbp/usd</td><td>1.4418347841461898</td></tr><tr><td>chf/usd</td><td>1.4488042231900922</td></tr><tr><td>btc/usd</td><td>10.269464495627822</td></tr>
    </table>
    '''
    assert (want_response == results_response.text, "Results should not differ from the baseline")

    rates_analyzer.terminate()
    rates_collector.terminate()
    backend.terminate()
    frontend.terminate()
    # rabbitmq.terminate()
