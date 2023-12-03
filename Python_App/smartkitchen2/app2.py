import controller
import util
import voice
from server import scan_subscriber

import pyttsx3

import threading
import time

# Maps ip -> (Name, T=valid item / F=distractor)
IP_TO_NAME = {
  "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
  "[0]C3:00:00:0B:1A:7A": ("Distractor", False),
  "[0]C3:00:00:0B:1A:7B" : ("Salt", True),
  "Placeholder" : ("1 Measure Cup", True),
  "[0]C3:00:00:0B:1A:86" : ("½ Measure Cup", True),
  "[0]C3:00:00:0B:1A:8A" : ("¼ Measure Spoon", True),
  "[0]C3:00:00:0B:1A:88" : ("Pan", True),
  "Placeholder" : ("Stirring Spoon", True),
  "[0]C3:00:00:0B:1A:87" : ("Timer", True),
  "[0]C3:00:00:0B:1A:89" : ("Bowl", True),
  "Placeholder" : ("Metal Spoon", True),
  "[0]C3:00:00:0B:1A:79" : ("Cork Hot Pad", True),
}


THRESH = -70
DEBUG = False
DEBUG_TAB = True


def millis():
    return time.time() * 1000

""" HELPER FUNCTIONS """

# Calibration function that returns average RSSI to a beaconAddr over n iters
def calibrateThresholds(iters, beaconAddr):
	
	rssiBuffer = [[],[],[]] # a [3 x iters] matrix
	for _ in range(0, iters):
		RSSI_TUPLE = SCAN()	# placeholder that obtains 1x3 arr of RSSI values to beaconAddr
		for reciever in range(0,len(RSSI_TUPLE)):
			rssiBuffer[reciever].append(RSSI_TUPLE[reciever])

	# Compute average RSSI per receiver
	return tuple(map((lambda x: sum(x)/len(x)), rssiBuffer))

def main():
    # Delta timing variables in millis
    PERIODIC_VOICE_DELTA_TIME = 5000  
    PERIODIC_VOICE_TIMER = millis()

    scan0_bound = -40
    scan1_inner_bound = -50
    scan1_outer_bound = -60
    scan2_bound = -70

    # Maps ip -> BeaconInfo while also performing trilateration logic
    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME, 
            scan0_bound, scan1_inner_bound, scan1_outer_bound, scan2_bound)


    scanner_thread = threading.Thread(target=scan_subscriber, args=(trilateration_table,))
    scanner_thread.start()

    while True:
        time.sleep(1)
        trilateration_table.print()
        print("\n")
        requiredItems = []
        proceed = True
        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
            if not beacon_info.required_item:
                beaconLocation = beacon_info.LocationEstimate
                voice.distractorPresent(beacon_info.name, beaconLocation)
                proceed = False
                break
            else:
                requiredItems.add(beacon_info.name)
        if proceed:
            # outputString = ""
            # for itemName in requiredItems:
            #     outputString = outputString + ", " + itemName
            voice.requires(requiredItems)


if __name__ == '__main__':
    main()
