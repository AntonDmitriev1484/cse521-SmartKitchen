from flask import Flask, request, jsonify
import logging
from util import LocationEstimate

SCANID_TARGET = 0
IP_TO_NAME = {
    "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
    "[0]C3:00:00:0B:1A:7A": ("Distractor", False),
    "[0]C3:00:00:0B:1A:7B": ("Salt", True),
    "Placeholder": ("1 Measure Cup", True),
    "[0]C3:00:00:0B:1A:86": ("½ Measure Cup", True),
    "[0]C3:00:00:0B:1A:8A": ("¼ Measure Spoon", True),
    "[0]C3:00:00:0B:1A:88": ("Pan", True),
    "Placeholder": ("Stirring Spoon", True),
    "[0]C3:00:00:0B:1A:87": ("Timer", True),
    "[0]C3:00:00:0B:1A:89": ("Bowl", True),
    "Placeholder": ("Metal Spoon", True),
    "[0]C3:00:00:0B:1A:79": ("Cork Hot Pad", True),
}
BEACONIP_TARGET = ['Oatmeal', 'Distractor', 'Timer', 'Salt']


# Defines the Flask server that receives fetch requests from the scanner
def scan_subscriber(trilateration_table):
    app = Flask('ScanSubscriber')

    #counter_max = 65*4

    with open('./drift-data.csv', 'w+') as file:

        #count = 0

        @app.route('/', methods=['POST'])
        def receive_json():
            try:
                scan = request.get_json()
                #if count < counter_max:
                if scan['device'] == SCANID_TARGET and (IP_TO_NAME[scan['addr']][0] in BEACONIP_TARGET):
                    # output beaconname, rssi to file

                    file.write(IP_TO_NAME[scan['addr']][0]+", "+str(scan['rssi'])+"\n")
                    file.flush()

                trilateration_table.update_rssi(scan['addr'], scan['rssi'], scan['device'])
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        app.logger.disabled = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        app.run(host='0.0.0.0',port=3000)
