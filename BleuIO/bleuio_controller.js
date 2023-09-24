import init_bleuIO from './bleuio_utils.js'

export default async function CreateScanner(bleuIO_device_path, interval) {

  let MAP_ADDR_TO_RSSI = {};

  const bleuIO = init_bleuIO(bleuIO_device_path);

  // Each time a gap scan result is printed on the terminal it will update our table
  function onNewGapScan(scan) {
    MAP_ADDR_TO_RSSI[scan.addr] = scan.rssi;
    console.log(scan);
  }

  bleuIO.onReadableEvent(onNewGapScan); // Prints out everything BleuIO outputs onto our terminal

  //await bleuIO.openPort();
  //bleuIO.writeData('ATV1'); // Turned verbose mode on/off
  await bleuIO.setCentralRole(); // This isnt working - the port.on listener is also not running.

  setInterval( async () => {
    await bleuIO.gapScan(interval); // Run gap scans at 3 sec interval
  }, interval*1000);

  // Once we have initialized the BleuIO device to work as a scanner
  // return a function that lets you read MAP_ADDR_TO_RSSI
  return () => {
            return MAP_ADDR_TO_RSSI;
          }
}
