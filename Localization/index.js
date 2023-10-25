import CreateScanner from '../BleuIO/bleuio_controller.js'

// const DevicePaths = ['COM4']; // For Windows

// RSSI Constants
const RSSI_PRESENT_THRESHOLD = -50;     // RSSI Strength threshold to specify as close 
                                        // enough to beacon to be "present"

const DevicePaths = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2'];
const SCAN_INTERVAL = 2;

// TODO: improve later with maybe a database and not hardcoded addresses
// Map containing ALL tag items
const TagItems = new Map([
    ['[0]C3:00:00:0B:1A:7C', "oatmeal"],
]);

// Set of valid tags (non-distractor)
const Valid_TagItems = new Set(
    '[0]C3:00:00:0B:1A:7C',
);

let AddressToDistance_ByDevice = {};
let AddressToRssi_ByDevice = {};


/*** TODO: ***
 * This "ForEach" may have to be reworked into a larger scope loop for central processing
 * of the BleuIO gapscans.
 * Currently, each gapscan is running trilateration and item detection individually,
 * for a total of 3 times.
 * This should only be done once by the central RPi processing portion of the loop,
 * so instead should look something more like:
 * 
 * -- INIT
 * (1) Initialize BleuIO receivers
 * -- LOOP
 * (2) Each receiver gapscans
 *   a. Update global update table of Item-->RSSI of respective receiver
 * (3) For each item in global update table
 *   a. Perform item detection
 *     i.  If on table, perform trilateration
 *     ii. Provide speaker cues
 *
 * So instead of creating anonymous BleuIO device objects
 * and relying on their periodic `update()` run, reference
 * each object and maybe implement an on-demand gapscan 
 * and collect/update data from the gapscan that can be
 * managed from a larger outside scope
 */

DevicePaths.forEach(
    async (recvPort) => { // CHECK: recvPort is the port of receiver?

        // Associate the device with an ADDR to RSSI map
        AddressToRssi_ByDevice[recvPort] = {};

        // Initialize the BleuIO device
        await CreateScanner(recvPort, SCAN_INTERVAL,
            // Pass in a function to run on every newline spit out by the gapscan
            (update) => {
                // Each new line spit out by the gap scan gives us an update
                // to our map. Apply update to the map that corresponds to our device.
                AddressToRssi_ByDevice[recvPort][update.addr] = update.rssi

                // Map containing the RSSI of the Address that just got updated
                // from the perspective of each device
                const RssiOfAddr_FromEachDevice =
                    Object.entries(AddressToRssi_ByDevice).reduce((acc, [currPort, AddressToRssi]) => {
                        acc[currPort] = AddressToRssi[update.addr]
                        return acc;
                    }, {});
                
                /* ITEM LOCALIZATION LOGIC */
                // Check if for item type on table
                if (DetectItem(update.addr, RssiOfAddr_FromEachDevice, recvPort)) {
                    // Trilaterate
                    let itemLoc = Trilaterate(update.addr, RssiOfAddr_FromEachDevice, recvPort);

                    // Check for distractor items
                    if (!Valid_TagItems.has(addr)) {
                        console.log("Distractor item of " + TagItems[update.addr] + " should be removed.");
                    } else {
                        console.log("Valid item of " + TagItems[update.addr] + " placed at " + itemLoc + " on table.");
                    }
                    
                } else {
                    console.log("Device " + update.addr + " is too far from receiver at " + recvPort);
                }

            }

        )
    });


/*** @params  
 *** addr: String           --> string address of BLE tag/item
 *** info: Set(String: Int) --> mapping of string ports and RSSI to item
 *** recv: String           --> port name of BleuIO receiver
 ***
 * Method to detect the presence of an item on the table. Works by checking for
 * RSSI within RSSI_PRESENT_THRESHOLD between all three BlueIO receivers.
 * Also provides is/is not distractor item checking.
 ***/
function DetectItem(addr, info, recv) {
    if (TagItems.has(addr)) {
        // True if combined RSSI from each device > RSSI_PRESENT_THRESHOLD*num_devices
        let RSSI_Sum = Object.values(info).reduce((acc, currRSSI) => {acc + currRSSI}, 0);
        return RSSI_Sum > RSSI_PRESENT_THRESHOLD*DevicePaths.length;
    }
}


/*** @params  
 *** addr: String           --> string address of BLE tag/item
 *** info: Set(String: Int) --> mapping of string ports and RSSI to item
 *** recv: String           --> port name of BleuIO receiver
 ***
 * Method to perform trilateration of an item's address, given RSSi to
 * each BleuIO receiver.
 * Performs trilateration via solving intersection of three 2D circles.
 ***/
function Trilaterate(addr, info, recv) {
    // Note: info formatted as: {'COM5': -62, 'COM4': -54, 'COM3': -52}

    // Given this information, you should be able to:
    // Update AddressToDistance map by trilateration

    //console.log(AddressToRssi_ByDevice);
    //console.log("Addr "+addr+" Info: "+JSON.stringify(info));


    // TODO: hardcoded for now, may want to create some database
    // read into a map between arg addr to a specific beacon (/w associated item)


    // Determine if polled addr is a valid item being tracked
    if (TagItems.has(addr)) {

        console.log('RSSI is of T3 -> [ACMO0 is ' + info['/dev/ttyACM0'] +
            '] [ACM1 is ' + info['/dev/ttyACM1'] + '] [ACM2 is ' + info['/dev/ttyACM2'] + ']');

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

        // Return coordinates (in inches)
        return (0,0);

    }

    // A little trilateration map here, find the distance
    // update AddressToDistance_ByDevice


}