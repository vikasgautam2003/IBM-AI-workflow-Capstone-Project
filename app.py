import argparse
import os
import re
import sys
from flask import Flask, jsonify, request, send_from_directory
from numpy import ndarray

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# import model specific functions and variables
from model import model_train, model_load, model_predict, MODEL_VERSION, MODEL_VERSION_NOTE

app = Flask(__name__)


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    return jsonify({'status': 1})


def convert_numpy_objects(res):
    # convert numpy objects to ensure they are serializable
    return {key: item.tolist() if isinstance(item, ndarray) else item
            for key, item in res.items()}


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    basic predict function for the API
    """

    # input checking
    req = request.get_json(silent=True)
    if not req:
        print("ERROR: API (predict): did not receive request data")
        return jsonify([])

    if 'query' not in req:
        print("ERROR API (predict): received request, but no 'query' found within")
        return jsonify([])

    # set the test flag
    test = False
    if 'mode' in req and req['mode'] == 'test':
        test = True

    # extract the query
    query = req['query']

    # load models and data once for all requested countries
    prefix = 'test' if test else 'sl'
    try:
        all_data, all_models = model_load(prefix=prefix, training=False)
    except Exception as e:
        print("ERROR: API (predict): {}".format(e))
        return jsonify({'error': str(e)}), 400

    print(query)
    result = {}
    if query['country'] == 'all':
        countries = sorted(all_models.keys())
    else:
        countries = query['country'].split(',')

    for country in countries:
        try:
            _result = model_predict(
                country, query['year'], query['month'], query['day'], test=test,
                prefix=prefix, all_models=all_models, all_data=all_data)
        except Exception as e:
            print("ERROR: API (predict): {}".format(e))
            return jsonify({'error': str(e)}), 400
        print("Predicted revenue for {} is {}".format(
            country, _result['y_pred'][0]))
        result[country] = convert_numpy_objects(_result)

    return(jsonify(result))


@app.route('/train', methods=['GET', 'POST'])
def train():
    """
    basic predict function for the API

    the 'mode' flag provides the ability to toggle between a test version and a 
    production verion of training
    """

    # check for request data
    req = request.get_json(silent=True)
    if not req:
        print("ERROR: API (train): did not receive request data")
        return jsonify(False)

    # set the test flag
    test = False
    if 'mode' in req and req['mode'] == 'test':
        test = True

    print("... training model")
    model_train(test=test)
    print("... training complete")

    return(jsonify(True))


@app.route('/logs/<filename>', methods=['GET'])
def logs(filename):
    """
    API endpoint to get logs
    """

    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.log", filename):
        print("ERROR: API (log): file requested was not a valid log file: {}".format(filename))
        return jsonify([])

    log_dir = os.path.realpath(os.path.join(".", "log"))
    if not os.path.isdir(log_dir):
        print("ERROR: API (log): cannot find log dir")
        return jsonify([])

    safe_filename = None
    for candidate in os.listdir(log_dir):
        candidate_path = os.path.join(log_dir, candidate)
        if os.path.isfile(candidate_path) and re.fullmatch(r"[A-Za-z0-9_.-]+\.log", candidate):
            if candidate == filename:
                safe_filename = candidate
                break

    if safe_filename is None:
        print("ERROR: API (log): file requested could not be found: {}".format(filename))
        return jsonify([])

    return send_from_directory(log_dir, safe_filename, as_attachment=True)


if __name__ == '__main__':

    # parse arguments for debug mode
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--debug", action="store_true", help="debug flask")
    args = ap.parse_args()

    if args.debug:
        app.run(debug=True, port=8080)
    else:
        app.run(host='0.0.0.0', threaded=True, port=8080)
