import init_bleuIO from './bleuio_utils.js'

export default async function CreateScanner(bleuIO_device_path, interval, func) {

  const bleuIO = init_bleuIO(bleuIO_device_path);

  // Each time a gap scan result is printed on the terminal it will update our table
  function onNewLine(scan) {
    func(scan);
  }

  bleuIO.onReadableEvent(onNewLine); // Binds a function to each new line BleuIO outputs onto serial
  await bleuIO.writeData('ATV1'); // Turned verbose mode on 
  await bleuIO.setCentralRole(); // Set central mode so you can perform gapscans

  setInterval( async () => {
    await bleuIO.gapScan(interval); // Run gap scans at an interval
  }, interval*1000);
}
