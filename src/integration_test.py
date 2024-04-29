#!/usr/bin/env python3

import requests
import time
import re
from subprocess import Popen

if __name__ == '__main__':
    print("Starting applications...")
    # rabbitmq = Popen('docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management')
    frontend = Popen('./applications/frontend_app.py')
    backend = Popen('./applications/backend_app.py')
    rates_collector = Popen('./applications/rates_collector_worker_app.py')
    rates_analyzer = Popen('./applications/rates_analyzer_worker_app.py')

    # Wait for all services to start.
    time.sleep(5)

    try:
        initiate_response = requests.post("http://127.0.0.1:5000/initiate_analysis", allow_redirects=False, data={
            "base_currency": "usd",
            "start_date": "2024-04-01",
            "end_date": "2024-04-25",
        })
        assert initiate_response.status_code == 302, "/initiate_analysis should return redirect on results page"
        analysis_id = re.findall("[0-9\-]+", initiate_response.text)[2]
        print("Got response: '" + initiate_response.text + "'")

        # Wait for analysis processing.
        time.sleep(5)

        results_response = requests.get("http://127.0.0.1:5000/get_results?analysis_id=" + analysis_id)
        assert results_response.status_code == 200, "/get_results should return 200"

        want_response = '''
    If no results shown, please refresh the page in a couple of seconds.
    <table>
    <tr><th>Currencies pair</th><th>2024-04-01</th><th>2024-04-25</th><th>Change(%)</th></tr>
    <tr><td>btc/usd</td><td>71079.68188714849</td><td>64459.98646340284</td><td>-9.313062816256801</td></tr><tr><td>chf/usd</td><td>1.1090543082822735</td><td>1.0932157522944521</td><td>-1.4281136522838467</td></tr><tr><td>gbp/usd</td><td>1.263566965896593</td><td>1.245607365625123</td><td>-1.4213413895896143</td></tr><tr><td>eur/usd</td><td>1.079325001800584</td><td>1.0698219052496825</td><td>-0.8804666374862102</td></tr>
    </table>
    '''
        print("Got response: '" + results_response.text + "'")
        assert want_response == results_response.text, "Results should not differ from the baseline"
    finally:
        print("Terminating applications...")
        rates_analyzer.terminate()
        rates_collector.terminate()
        backend.terminate()
        frontend.terminate()
        # rabbitmq.terminate()
