import init_bleuIO from './bleuio_utils.js'

export default async function CreateScanner(bleuIO_device_path, interval, onNewLine) {

  const bleuIO = init_bleuIO(bleuIO_device_path);

  // Each time a gap scan result is printed on the terminal it will update our table
  bleuIO.onReadableEvent(onNewLine); // Binds a function to each new line BleuIO outputs onto serial

  await bleuIO.writeData('ATV1'); // Turned verbose mode on 
  await bleuIO.setCentralRole(); // This isnt working - the port.on listener is also not running.

  setInterval( async () => {
    await bleuIO.gapScan(interval); // Run gap scans at an interval
  }, interval*1000);

  // Once we have initialized the BleuIO device to work as a scanner
  // return a function that lets you read MAP_ADDR_TO_RSSI

}
