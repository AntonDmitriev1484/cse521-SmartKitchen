import CreateScanner from './bleuio_controller.js'
import { SerialPort } from "serialport";

import { express } from express;


// const app = express();
// const port = 3000;

const DevicePaths = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2'];
const SCAN_INTERVAL = 1;
const SUBSCRIBER_URL = 'http://172.27.84.110:3000';

const DEVSERIAL_TO_ID = {
  
}

// Maps ip -> (Name, T=valid item / F=distractor)
const IP_TO_NAME = {
  "[0]C3:00:00:0B:1A:7C": ("Oatmeal", true),
  "[0]C3:00:00:0B:1A:7A": ("Distractor", false),
  "[0]C3:00:00:0B:1A:7B" : ("Salt", true),
  "Placeholder" : ("1 Measure Cup", true),
  "[0]C3:00:00:0B:1A:86" : ("½ Measure Cup", true),
  "[0]C3:00:00:0B:1A:8A" : ("¼ Measure Spoon", true),
  "[0]C3:00:00:0B:1A:88" : ("Pan", true),
  "Placeholder" : ("Stirring Spoon", true),
  "[0]C3:00:00:0B:1A:87" : ("Timer", true),
  "[0]C3:00:00:0B:1A:89" : ("Bowl", true),
  "Placeholder" : ("Metal Spoon", true),
  "[0]C3:00:00:0B:1A:79" : ("Cork Hot Pad", true),
}

// app.get('/get-calibration-point', (req, res) => {
// })


//app.get('/run', (req, res) => {
  DevicePaths.forEach(
    async (port) => { // CHECK: port is the port of receiver?
        console.log(`Initializing ${port}`);
        // Associate the device with an ADDR to RSSI map

        // Initialize the BleuIO device
        await CreateScanner(port, SCAN_INTERVAL,
            // Pass in a function, POSTs each ser_line to a Python server
            (ser_line) => {
              
                if (IP_TO_NAME[ser_line.addr]) {

                  const update = {
                    'device':port,
                    'addr':ser_line.addr,
                    'rssi':ser_line.rssi
                  }
                    // If this is one of our BLE beacons
                    console.log(`Sending ser_line from ${port}`);
                    console.log(ser_line);

                    fetch(SUBSCRIBER_URL, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json'
                      },
                      body: JSON.stringify(update)
                    })  
                    .then(response => {
                      return response.json();
                    })
                    .then(data => {
                      console.log(data);
                    })
                    .catch(error => {
                      console.error('Fetch error:', error);
                    });

                }

                // Each new line spit out by the gap scan gives us an ser_line
                // to our map. Apply ser_line to the map that corresponds to our device.
                // AddressToRssi_ByDevice[port][ser_line.addr] = ser_line.rssi
            }
        )
    }
    );


//})


