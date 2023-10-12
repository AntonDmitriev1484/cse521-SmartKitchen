import CreateScanner from '../BleuIO/bleuio_controller.js'

// const DevicePaths = ['COM4']; // For Windows

const DevicePaths = ['/dev/tty/ACM0']
const SCAN_INTERVAL = 2;

let AddressToDistance_ByDevice = {};
let AddressToRssi_ByDevice = {};

DevicePaths.forEach( 
    async (name) => { 

        // Associate the device with an ADDR to RSSI map
        AddressToRssi_ByDevice[name] = {};

        // Initialize the BleuIO device
        await CreateScanner(name, SCAN_INTERVAL, 
            // Pass in a function to run on every newline spit out by the gapscan
            (update) => {
                    // Each new line spit out by the gap scan gives us an update
                    // to our map. Apply update to the map that corresponds to our device.
                    AddressToRssi_ByDevice[name][update.addr] = update.rssi
                    
                    // Re-run trilateration
                    
                    // Map containing the RSSI of the Address that just got updated
                    // from the perspective of each device
                    const RssiOfAddr_FromEachDevice = 
                        Object.entries(AddressToRssi_ByDevice).reduce( (acc, [name, AddressToRssi]) => {
                            acc[name] = AddressToRssi[update.addr]
                            return acc;
                        }, {});

                    Trilaterate(update.addr, RssiOfAddr_FromEachDevice);
            }

        )
    })

function Trilaterate(addr, info) {   
    // ( SOME_ADDR, {'COM5': -62, 'COM4': -54, 'COM3': -52} )

    // Given this information, you should be able to:
    // Update AddressToDistance map by trilateration

    //console.log(AddressToRssi_ByDevice);

    const TargetName = '[0]C3:00:00:0B:1A:7C'
    // Note: The MINEW beacons also have their own names, this one is 'T3'
    // I think you can manually set names through the BeaconSET app
    if (addr == TargetName) {
        console.log('RSSI is of T3 is: ' + info['/dev/tty/ACM0']);
    }

    // A little trilateration map here, find the distance
    // update AddressToDistance_ByDevice


}