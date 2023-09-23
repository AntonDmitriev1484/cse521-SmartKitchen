import init_bleuIO from './dongle_rw.js'

// const DEVICE_PATH = 'dev/...'; // Linux devices use dev/...
const DEVICE_PATH = 'COM5'; // Windows devices use COM
const bleuIO = init_bleuIO(DEVICE_PATH);

// Sometimes you just need to run the node script through elevated (run as admin) command prompt?
// Referencing commands in: https://www.bleuio.com/blog/indoor-positioning-systems-based-on-ble-beacons/
// Need to manually write these commands: https://www.bleuio.com/getting_started/docs/commands/


try {
    const portUtils = bleuIO(DEVICE_INSTANCE_PATH);