import init_bleuIO from './dongle_rw.js'

// const DEVICE_PATH = 'dev/...'; // Linux devices use dev/...
const DEVICE_PATH = 'COM5'; // Windows devices use COM
const bleuIO = init_bleuIO(DEVICE_PATH);

// Sometimes you just need to run the node script through elevated (run as admin) command prompt?
// Referencing commands in: https://www.bleuio.com/blog/indoor-positioning-systems-based-on-ble-beacons/
// Need to manually write these commands: https://www.bleuio.com/getting_started/docs/commands/

// Note: Issuing a filter by RSSI command seems a bit unnecessary

await bleuIO.setCentralRole();
let data = await bleuIO.readData();
console.log('Setting central role '+data);
await bleuIO.gapScan();
data = await bleuIO.readData();
console.log('Gapscan result '+data);