# How to Run This Project

Step-by-step instructions for setting up, training, testing and serving the revenue forecasting models.

## 1. Requirements

- Python 3.12 or newer (tested on 3.14)
- Git
- Docker (optional, only for running in a container)

## 2. Get the code

```bash
git clone https://github.com/vikasgautam2003/IBM-AI-workflow-Capstone-Project.git
cd IBM-AI-workflow-Capstone-Project
```

## 3. Set up a virtual environment

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run every command below from the project root, with the virtual environment active.

## 4. Project layout

| Path | What it contains |
|---|---|
| `data/cs-train/` | Training invoices (JSON), plus pre-aggregated time series in `ts-data/` |
| `data/cs-production/` | Later invoices, used to simulate production data |
| `src/cslib.py` | Data loading and feature engineering |
| `src/model.py` | Model training, loading and prediction (also a command-line tool) |
| `src/logger.py` | Train and predict logging |
| `src/monitoring.py` | Drift and outlier monitoring |
| `app.py` | Flask API |
| `unittests/` | Model, logger and API tests |
| `models/` | Trained models, created on first training (not committed) |
| `log/` | Train and predict log files |

## 5. Train the models

There are two training modes:

- **test**: quick; trains on a 30% sample, only for `all` and `united_kingdom`. Models are saved as `models/test-*.joblib`.
- **prod**: full data; trains the countries you list. Models are saved as `models/sl-*.joblib`.

```bash
# quick test models
python3 src/model.py -t test -c united_kingdom

# production models for one or more countries
python3 src/model.py -t prod -c united_kingdom,portugal,all
```

After training, the command prints a sample prediction for 2019-06-05.

Options:

| Flag | Values | Default |
|---|---|---|
| `-t`, `--training` | `test` or `prod`; omit to load already-trained models | none |
| `-m`, `--model` | `rf` (RandomForest) or `et` (ExtraTrees) | `et` |
| `-s`, `--scaler` | `ss` (StandardScaler) or `rs` (RobustScaler) | `rs` |
| `-c`, `--countries` | Comma-separated country names (required) | none |

Available countries: `all`, `eire`, `france`, `germany`, `hong_kong`, `netherlands`, `norway`, `portugal`, `singapore`, `spain`, `united_kingdom`.

## 6. Run the API

```bash
python3 app.py        # normal mode
python3 app.py -d     # debug mode (auto-reload)
```

The server listens on http://localhost:8080. Leave it running in its own terminal.

### Check it is up

```bash
curl http://localhost:8080/ping
# {"status":1}
```

### Train through the API

```bash
curl -X POST http://localhost:8080/train \
  -H "Content-Type: application/json" \
  -d '{"mode": "test"}'
# true
```

Use `"mode": "prod"` to train production models for every country. That takes several minutes.

### Predict

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"mode": "test", "query": {"country": "united_kingdom", "year": "2019", "month": "06", "day": "05"}}'
```

- `country` can be one country, a comma-separated list (`"united_kingdom,all"`), or `"all"` for every country that has a trained model.
- `year`, `month` and `day` must be strings of digits. If the date is outside the data range, the nearest available date is used.
- `mode` picks which models to use: `"test"` or `"prod"` (the default). Train that mode first.

The response gives the predicted revenue for the next 30 days:

```json
{"united_kingdom": {"y_pred": [156793.88], "y_proba": []}}
```

An unknown country, or a mode with no trained models, returns HTTP 400 with an `error` message.

### Download a log file

```bash
curl -O http://localhost:8080/logs/example-train-2026-9.log
```

Log names follow `<prefix>-<train|predict>-<year>-<month>.log`. See the `log/` folder for the files that exist.

## 7. Run the tests

Start the API server first (step 6), otherwise the 6 API tests are skipped. Then, in a second terminal:

```bash
python3 run-tests.py
```

All 14 tests should pass. To run one group or one test:

```bash
python3 -m unittest unittests/ModelTests.py
python3 -m unittest unittests/LoggerTests.py
python3 -m unittest unittests/ApiTests.py
python3 -m unittest unittests.ModelTests.ModelTest.test_02_load
```

## 8. Monitor for drift

Train production models for `united_kingdom` first (step 5), then run:

```bash
python3 src/monitoring.py
```

It prints the outlier and Wasserstein-distance thresholds used to detect drift in new data.

## 9. Run with Docker

```bash
docker build -t ai-workflow-capstone .
docker run -p 8080:8080 ai-workflow-capstone
```

The API is then available at http://localhost:8080, as in step 6. Models trained inside the container are lost when it stops.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `Models with prefix 'sl' cannot be found did you train?` | Train production models first (step 5), or use `"mode": "test"` after test training. |
| `model for country '...' could not be found` | That country wasn't trained. Test mode only trains `all` and `united_kingdom`. |
| `Address already in use` on port 8080 | Another server is still running. Stop it, or on macOS find it with `lsof -i :8080`. |
| API tests show as skipped | The server isn't running. Start `python3 app.py` first. |
| `ModuleNotFoundError` | The virtual environment isn't active, or `pip install -r requirements.txt` wasn't run. |
