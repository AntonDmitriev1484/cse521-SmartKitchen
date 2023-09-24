import CreateScanner from '../BleuIO/bleuio_controller.js'

const device_paths = ['COM5'];
// Windows devices use COM
// Linux devices use dev/...

const SCAN_INTERVAL = 2;

function buildTrilaterator() {

    // Locally maintain all RSSI maps
    const RSSI_MAPS = device_paths.reduce( (path, acc)=> {
        return acc[path] = {};
    }, {});
    // Creates a map of device -> device RSSI_MAP



    const RSSI_MAPS_UPDATERS = device_paths.map( (path)=> {
        return (updated_map) => {
            RSSI_MAPS[path] = updated_map;
        }
    });

    // I think I'm overengineering this a little lol

    
}

const RSSI_MAP_GETTERS = device_paths.map( async (path) => {
    return await CreateScanner(path, SCAN_INTERVAL)

    }
    );
// One map per BleuIO device. Each maps a MAC address to its RSSI.
// These maps are updated every SCAN_INTERVAL number of seconds.
// Each function in this array lets you read from the corresponding device's map.

// Ok the while true loop was deadass breaking it what the fuck