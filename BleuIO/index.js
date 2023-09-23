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
console.log(data);
// So its just not calling the event listener
// port is NOT OPEN?
await bleuIO.gapScan(3);

// Its not writing gapScan?

// Ok I think I need to switch writeData over to uses promises
// this is bizzare

// try {
//   await bleuIO.gapScan(3);
//   let data2 = await bleuIO.readData();
//   console.log('data received');
//   console.log(data2);
//   // parseGapScanData(data);
// }
// catch (err) {
//   console.log(err);
// }



// setInterval(
//   async () => {
//     await bleuIO.gapScan(3);
//     data = await bleuIO.readData();
//     console.log(data);
//     parseGapScanData(data);

//   }, 3000
// );

function parseGapScanData(data) {
  const macAddressPattern = /\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b/;
  const rssiPattern = /-\d+/;

  const parsed_data = data.map((str) => {
    console.log(str);
    let rssi = parseInt(str.match(rssiPattern),10);
    return (str.match(macAddressPattern), rssi)
  })

  // const macAddressMatches = data.match(macAddressPattern);
  // const rssiMatches = data.match(rssiPattern);

  console.log(parsed_data);

  return parsed_data;
}

// Ok it seems to be memory leaking? Why lol?


// Note: RSSI will come up as negative because it indicates
// how much signal strength has been lost.