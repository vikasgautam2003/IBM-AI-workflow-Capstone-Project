# IBM AI Workflow Capstone: Revenue Forecasting

Author: Vikas Gautam

Predicts revenue for the next 30 days per country, and serves the models through a Flask API.

## Setup
```
pip install -r requirements.txt
```

# Project Execution Instructions
## Run the model directly
Run from the project root, e.g. `python3 src/model.py -t test -c united_kingdom`.

```
usage: model.py [-h] [-t {test,prod}] [-m {rf,et}] [-s {ss,rs}] -c COUNTRIES

options:
  -h, --help            show this help message and exit
  -t {test,prod}, --training {test,prod}
                        Train either a test or production model. Omitting this implies loading an already-trained model
  -m {rf,et}, --model {rf,et}
                        (rf) RandomForestRegressor or (et) ExtraTreesRegressor (default)
  -s {ss,rs}, --scaler {ss,rs}
                        (ss) StandardScaler or (rs) RobustScaler (default)
  -c COUNTRIES, --countries COUNTRIES
                        Comma separated list of countries to predict revenue
```

## Run unit tests
### Run all tests
```
python3 run-tests.py
```
### Model Tests
All tests: `python3 -m unittest unittests/ModelTests.py`

Specific test: `python3 -m unittest unittests.ModelTests.ModelTest.test_02_load`

### Logger Tests
All tests: `python3 -m unittest unittests/LoggerTests.py`

Specific test: `python3 -m unittest unittests.LoggerTests.LoggerTest.test_04_predict`

### API Tests
All tests: `python3 -m unittest unittests/ApiTests.py`

Specific test: `python3 -m unittest unittests.ApiTests.ApiTest.test_04_predict_all`

The API tests are skipped unless the server is running (`python3 app.py`).

## Performance monitoring
Run `python3 src/monitoring.py`.

## API Documentation

Make sure that you run the server with `python3 app.py` or `python3 app.py -d`. It listens on port 8080.

With Docker:
```
docker build -t ai-workflow-capstone .
docker run -p 8080:8080 ai-workflow-capstone
```


      Request type    | Key            | Description
     =======================================================================
      /train          | mode           | Training mode - test or prod
     -----------------+----------------+------------------------------------
                      | query          | Query for model, must be a dict containing 
      /predict        |                | 'country','year','month','day' as keys, with their
                      |                | values as strings.
                      | mode           | Model to be used - test or prod
     -----------------+----------------+------------------------------------
      /logs/<filename>| filename       | Name of log file to retrieve
     -----------------+----------------+------------------------------------
