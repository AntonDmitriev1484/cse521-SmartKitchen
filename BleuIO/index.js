import init_bleuIO from './dongle_rw.js'

// const DEVICE_PATH = 'dev/...'; // Linux devices use dev/...
const DEVICE_PATH = 'COM4'; // Windows devices use COM
const bleuIO = init_bleuIO(DEVICE_PATH);

// Sometimes you just need to run the node script through elevated (run as admin) command prompt?
// Referencing commands in: https://www.bleuio.com/blog/indoor-positioning-systems-based-on-ble-beacons/
// Need to manually write these commands: https://www.bleuio.com/getting_started/docs/commands/

// Note: Issuing a filter by RSSI command seems a bit unnecessary

bleuIO.letRead(); // Prints out everything BleuIO outputs onto our terminal

//bleuIO.writeData('ATV1'); // Turn verbose mode on
await bleuIO.setCentralRole();

//let data = await bleuIO.readData();
await bleuIO.gapScan(3);
//data = await bleuIO.readData();

//Ok, so it was actually just working the whole time, but the person who wrote this API is a little stupid.
