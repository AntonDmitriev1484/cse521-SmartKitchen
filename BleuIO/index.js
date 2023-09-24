import init_bleuIO from './bleuio_utils.js'

// const DEVICE_PATH = 'dev/...'; // Linux devices use dev/...
const DEVICE_PATH = 'COM4'; // Windows devices use COM
const bleuIO = init_bleuIO(DEVICE_PATH);

// Ok I'll figure out all the parallelism involved later
// this is enough to test with one sensor for now.
// Maybe just wrap this ina BLEUIO controller json
// and you'll be able to spin these up elsewhere

let MAP_ADDR_TO_RSSI = {};

// Each time a gap scan result is printed on the terminal it will update our table
function onNewGapScan(scan) {
  MAP_ADDR_TO_RSSI[scan.addr] = scan.rssi;
  console.log(scan);
  // No way of pruning a BLE device that has gone offline from the map
  // but I think that should be fine
}

// Lets you read the current map from another file
function fetchRSSIMap() {
  return MAP_ADDR_TO_RSSI;
}

bleuIO.onReadableEvent(onNewGapScan); // Prints out everything BleuIO outputs onto our terminal

//bleuIO.writeData('ATV1'); // Turned verbose mode on/off
await bleuIO.setCentralRole();

const SCAN_INTERVAL = 3;
setInterval( async () => {
  await bleuIO.gapScan(SCAN_INTERVAL); // Run gap scans at 3 sec interval
}, SCAN_INTERVAL*1000);