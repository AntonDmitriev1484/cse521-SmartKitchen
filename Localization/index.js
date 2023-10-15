import CreateScanner from '../BleuIO/bleuio_controller.js'

// const DevicePaths = ['COM4']; // For Windows

const DevicePaths = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
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
    //console.log("Addr "+addr+" Info: "+JSON.stringify(info));


    // TODO: hardcoded for now, may want to create some database
    // read into a map between arg addr to a specific beacon (/w associated item)
    const TargetName = '[0]C3:00:00:0B:1A:7C'
    
    // TODO: process database into set
    ValidTargetNames = Set();
    ValidTargetNames.add(TargetName);

    // Determine if polled addr is a valid item being tracked
    if (ValidTargetNames.has(addr)) {
        console.log('RSSI is of T3 -> [ACMO0 is ' + info['/dev/ttyACM0']+
        '] [ACM1 is '+ info['/dev/ttyACM1'] + '] [ACM2 is '+ info['/dev/ttyACM2']+']');

        /* BEGIN TRILATERATION LOGIC */
        /*
         * Works essentially by solving the intersection of three circles
         *
         * We know:
         * - Absolute position of each receiver in frame from some origin of the table
         *      + let origin be bottom-left of table
         * - RSSI from beacon to each receiver
         *      + can compute distance from RSSI
         * 
         * This gives us the three circles in our absolute grid of (0,0) being the B-L
         * corner of table as such:
         * - RSSI_d(1-3):   distance between beacon to receiver 1-3
         * - h_(1-3):       x_abs pos of receiver 1-3 wrt org
         * - k_(1-3):       y_abs pos of receiver 1-3 wrt org
         * (1) RSSI_d1^2 = (x-h_1)^2 + (y-k_1)^2
         * (2) RSSI_d2^2 = (x-h_2)^2 + (y-k_2)^2
         * (3) RSSI_d3^2 = (x-h_3)^2 + (y-k_3)^2
         * 
         * Becomes a problem of solving a system of equations with a guaranteed 
         * solution (impossible for all three circles to not intersect given
         * all receivers will be pinging an individual beacon)
         * 
         * One possible method of doing this is by reducing problem to intersection
         * of two lines b/w any two pairs of circles' chords
         * - in the very unlikely theoretical event of a degenerate singular
         *   intersection between a pair of circles, we can just reduce it to
         *   a vertical or horizontal line (don't want to deal with floating
         *   point precision if we can help it)
         * 
         * Then easily becomes the process of:
         * 1. pick one root circle A (randomly)
         *  - let the other circles be B and C
         * 2. calculate intersections of A to B, A to C
         *  - simple 2-sys equation with two/one real soln (circles guarantee to intersect) 
         * 3. calculate intersect of the two lines per AB and AC soln
         *
         * Soln will be returned in terms of abs pos from (0,0) if we keep
         * the position of receiver in program memory as abs from same origin
         * 
         */


    }

    // A little trilateration map here, find the distance
    // update AddressToDistance_ByDevice


}