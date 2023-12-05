from flask import Flask, request, jsonify
import logging
from util import LocationEstimate

# Defines the Flask server that receives fetch requests from the scanner
def scan_subscriber(trilateration_table):
    app = Flask('ScanSubscriber')
    @app.route('/', methods=['POST'])
    def receive_json():
        try:
            scan = request.get_json()
            trilateration_table.update_rssi(scan['addr'], scan['rssi'], scan['device'])
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    app.logger.disabled = True
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    app.run(host='0.0.0.0',port=3000)
