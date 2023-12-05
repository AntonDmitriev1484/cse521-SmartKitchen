import controller
import util
from util import average
import voice
from server import scan_subscriber

import pyttsx3

import threading
import time
import requests


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



def calibrate_bounds_by_beacon(trilateration_table):
    time.sleep(6) # Wait to get an average going
    # Get the distractor BeaconInfo
    trilateration_table.print()

    beacon_on_sensor = {
         0: "[0]C3:00:00:0B:1A:87", # 0 opposite Timer
         1: "[0]C3:00:00:0B:1A:88", # 1 opposite Pan
         2: "[0]C3:00:00:0B:1A:79", # 2 opposite Cork hot pad
         3: "[0]C3:00:00:0B:1A:8A", #3 opposite 1/4 Measure Spoon
    }
    

    bounds = [
         trilateration_table.get(beacon_on_sensor[1]).rssi_array[0],
         trilateration_table.get(beacon_on_sensor[2]).rssi_array[1],
         trilateration_table.get(beacon_on_sensor[3]).rssi_array[2],
         trilateration_table.get(beacon_on_sensor[0]).rssi_array[3]
    ]
    # for i in range(0,4):
    #     bounds.append(trilateration_table.get(beacon_on_sensor[i]).rssi_array[i])

    avg = average(bounds)
    for i in range(0,4):
        bounds[i] = avg
    trilateration_table.init_bounds(bounds)


        

def main():
    # Delta timing variables in millis
    PERIODIC_VOICE_DELTA_TIME = 5000  
    PERIODIC_VOICE_TIMER = millis()


    # Maps ip -> BeaconInfo while also performing trilateration logic
    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME)


    scanner_thread = threading.Thread(target=scan_subscriber, args=(trilateration_table,))
    scanner_thread.start()

    # Blocks for 6 seconds to callibrate the table's RSSI bounds
    calibrate_bounds_by_beacon(trilateration_table)

    while True:
        trilateration_table.print()
        print("\n")
        time.sleep(1)

        # Temporarily commenting out Jason code (UP TO DATE)
        # time.sleep(5)
        # trilateration_table.print()
        # print("\n")
        # requiredItems = []
        # proceed = True
        # for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
        #     if not beacon_info.required_item and not beacon_info.loc_estimate == util.LocationEstimate.OFF:
        #         beaconLocation = beacon_info.loc_estimate
        #         voice.distractorPresent(beacon_info.name, beaconLocation)
        #         proceed = False
        #         break
        #     elif beacon_info.required_item:
        #         if beacon_info.loc_estimate == util.LocationEstimate.OFF:  # CHANGE THIS
        #             print("beacon name: ")
        #             print(beacon_info.name)
        #             requiredItems.append(beacon_info.name)
        # if proceed:
        #     voice.requires(requiredItems)

if __name__ == '__main__':
    main()
