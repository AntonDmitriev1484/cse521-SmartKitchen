import CreateScanner from './bleuio_controller.js'
import { SerialPort } from "serialport";
import * as child from 'child_process';
import XRegExp from "xregexp";

// import { express } from express;


// Connecting in order, should be consistent with ACM tag

const DevicePaths = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2','/dev/ttyACM3'];
const SCAN_INTERVAL = 1;
const SUBSCRIBER_URL = 'http://172.27.177.63:3000';

// AT+DIS to find the serial number of the BleuIO running on each port
// You can run ./findDev.sh on the pi to figure out the serial code of each pi
// Try to figure out a way to do this in js


// Maps ip -> (Name, T=valid item / F=distractor)
const IP_TO_NAME = {
  "[0]C3:00:00:0B:1A:7C": ("Oatmeal", true),
  "[0]C3:00:00:0B:1A:79": ("Distractor", false),
  "[0]C3:00:00:0B:1A:7B" : ("Salt", true),
//   "Placeholder" : ("1 Measure Cup", true),
  "[0]C3:00:00:0B:1A:86" : ("½ Measure Cup", true),
  "[0]C3:00:00:0B:1A:8A" : ("¼ Measure Spoon", true),
  "[0]C3:00:00:0B:1A:88" : ("Calibrator", true),
//   "Placeholder" : ("Stirring Spoon", true),
  "[0]C3:00:00:0B:1A:87" : ("DistractorV2", true), // Originally timer
  "[0]C3:00:00:0B:1A:89" : ("Bowl", true),
//   "Placeholder" : ("Metal Spoon", true),
//   "[0]C3:00:00:0B:1A:XX" : ("Cork Hot Pad", true),
}

const SERID_TO_SENSID = {
  "4048FDE85405": 0, // Top right
  "4048FDE85428": 1, // Bottom right
  "4048FDE853C6": 2, // Bottom left
  "4048FDE85A27": 3, // Top left
}


child.exec('~/findDev.sh', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }

  // Initialization code to map DevSerial paths /dev/ttyACM0 to physical sensor 
  // ids by getting their serial numbers with a bash script
  console.log('Command output:', stdout);
  let lines = stdout.split('\n');

  let DEVPATH_TO_SENSID = {};

  // Match: /dev/ttyACM2 - Smart_Sensor_Devices_BleuIO_4048FDE853C6
  const reg = new RegExp(/^(.*) - (.*)$/);

  console.log(lines);
  lines.pop()

  lines.forEach( (line) => {

    let [full, devpath, serid] = line.match(reg);
    serid = serid.match(/.{12}$/);
    // last 12 char

    console.log(devpath +" | "+serid);

    DEVPATH_TO_SENSID[devpath] = SERID_TO_SENSID[serid]
  })

  console.log(DEVPATH_TO_SENSID);

  DevicePaths.forEach(
    async (port) => { // CHECK: port is the port of receiver?
        console.log(`Initializing ${port}`);
        // Associate the device with an ADDR to RSSI map

        // Initialize the BleuIO device
        await CreateScanner(port, SCAN_INTERVAL,
            // Pass in a function, POSTs each ser_line to a Python server
            (ser_line) => {
             	// PATHLOSS DEBUG: hardcode check for our BLE calibration tag ([0]C3:00:00:0B:1A:88) 
                //if (ser_line.addr == "[0]C3:00:00:0B:1A:79") {

                // Sometimes it gets 'undefined' as its ser_line
                //console.log(" Ser_line addr is: "+ser_line.addr+" map access gives: "+IP_TO_NAME[ser_line.addr])
                // console.log(IP_TO_NAME[ser_line.addr][0] +" "+ IP_TO_NAME[ser_line.addr][0])
                if (IP_TO_NAME[ser_line.addr] !== undefined) {
              
                  const update = {
                    'device':DEVPATH_TO_SENSID[port],
                    'addr':ser_line.addr,
                    'rssi':ser_line.rssi
                  }

                  // if ( ser_line.addr === "[0]C3:00:00:0B:1A:79") {
                  //   console.log("SENDING DISTRACTOR INFO");
                  // }
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
  });


