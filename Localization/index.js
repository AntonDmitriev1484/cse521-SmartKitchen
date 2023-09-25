import CreateScanner from '../BleuIO/bleuio_controller.js'

const DevicePaths = ['COM4'];
const SCAN_INTERVAL = 2;

let AddressToDistance = {};
let AddressToRssi_ByDevice = {};

DevicePaths.forEach( 
    async (name) => { 

        AddressToRssi_ByDevice[name] = {}; // Register the device with an ADDR to RSSI map

        // Initialize a BleuIO device
        await CreateScanner(name, SCAN_INTERVAL, 

            // Pass in a function to run on every gapscan
            (update) => {
                
                    // Each new line spit out by the gap scan gives us an update
                    // to our map.

                    // Apply update to the map that corresponds to our device

                    AddressToRssi_ByDevice[name][update.addr] = update.rssi
                    // Run trilateration again
                    Trilaterate();
            }

        )
    })

function Trilaterate() {

    console.log(AddressToRssi_ByDevice);
    // Assume all of AddressToRssi_ByDevice is always up to date
    // Given this information, you should be able to:
    // Update AddressToDistance map by trilateration

}