# exchange-rates-analyzer
## How to run
- Clone repository `git clone https://github.com/eshemchik/exchange-rates-analyzer.git` and navidate to it `cd exchange-rates-analyzer`
- Set up environment `python3 -m venv venv && source venv/bin/activate`
- Install dependencies `pip install -r requirements.txt`
- Start RabbitMQ `docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management`
- Start all the services `cd src`
  - `./applications/frontend_app.py`
  - `./applications/backend_app.py`
  - `./applications/rates_collector_worker_app.py`
  - `./applications/rates_analyzer_worker_app.py`
- Navigate to `http://127.0.0.1:5000` and start your analyze
  - Don't forget to refresh results page if the results table is empty.
 
## Testing
- Unit tests: `./run_unit_tests.sh`
- Integration test: `./integration_test.py`
  - Important: for integration test RabbitMQ should be running 
