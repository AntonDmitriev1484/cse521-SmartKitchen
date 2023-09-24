import init_bleuIO from './bleuio_utils.js'

export default async function CreateScanner(bleuIO_device_path, interval) {

  let MAP_ADDR_TO_RSSI = {};

  const bleuIO = init_bleuIO(bleuIO_device_path);

  // Each time a gap scan result is printed on the terminal it will update our table
  function onNewGapScan(scan) {
    MAP_ADDR_TO_RSSI[scan.addr] = scan.rssi;

    console.log('s'+scan);
    console.log(MAP_ADDR_TO_RSSI); 
    // Need to see if previous devices ever get updated
    // or if this only searches for new devices.
  }

  // I only think GAPSCAN ever recognizes new devices
  // it will never re-find old ones

  // So, I think we need to do an AT Target Scan
  // to do this we make a map of the the non-distractor tags
  // figure out what their MAC address is
  // and only target scan these addresses.
  // = note: you can only target scan 3 things at a time.
  // Problem: This doesn't really let us detect distractors

  // Surely there must be some way to just re-scan everything at a specific interval
  // Figure out how to ssh into the dongle
  // try issuing commands from there.

  bleuIO.onReadableEvent(onNewGapScan); // Prints out everything BleuIO outputs onto our terminal

  //await bleuIO.openPort();
  await bleuIO.writeData('ATV1'); // Turned verbose mode on/off
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
