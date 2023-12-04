import controller
import util
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
    # use the distractor to callibrate bounds
    # Basically just look at its average rssi values from each scanner, and return those in an array

    time.sleep(6) # Wait to get an average going
    # Get the distractor BeaconInfo
    trilateration_table.print()
    info = trilateration_table.get("[0]C3:00:00:0B:1A:88")
    [scan0_bound, scan1_inner_bound, scan2_bound] = info.rssi_array
    # Caution! This will be very incorrect if the bounds 
    # aren't mapped to the correct physical sensors

    scan1_outer_bound = (scan2_bound + scan0_bound) / 2

    # Check receiver orientation consistent
    # Check serial_id corresponds to physical device

    
    trilateration_table.init_bounds(scan0_bound, scan1_inner_bound, scan1_outer_bound, scan2_bound)


        

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
        time.sleep(5)
        trilateration_table.print()
        print("\n")
        requiredItems = []
        proceed = True
        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
            if not beacon_info.required_item and not beacon_info.loc_estimate == util.LocationEstimate.OFF:
                beaconLocation = beacon_info.loc_estimate
                voice.distractorPresent(beacon_info.name, beaconLocation)
                proceed = False
                break
            elif beacon_info.required_item:
                if beacon_info.loc_estimate == util.LocationEstimate.OFF:  # CHANGE THIS
                    print("beacon name: ")
                    print(beacon_info.name)
                    requiredItems.append(beacon_info.name)
        if proceed:
            # outputString = ""
            # for itemName in requiredItems:
            #     outputString = outputString + ", " + itemName
            voice.requires(requiredItems)




    # --- CODE FOR TTS DEMO COMMENTED OUT
    # while True:
    #     time.sleep(1)
    #     # For every item in table
    #
    #     trilateration_table.print()
    #     for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
    #
    #         # Update RSSI values between item and all receivers
    #         sum = 0
    #         n = 0
    #         for rssi in beacon_info.rssi_array:
    #             if rssi:
    #                 sum += rssi
    #                 n += 1
    #         avg = sum / n
    #
    #         # Determine if item is on table or not
    #         isItemOnTable = False
    #         if avg > THRESH:
    #             isItemOnTable = True
    #             print(f"{beacon_info.name}: {avg} is on table") if DEBUG else None
    #         else:
    #             print(f"{beacon_info.name}: {avg} is not on table") if DEBUG else None
    #
    #
    #         ### VOICE SEQUENCES
    #
    #         # Periodic voice cues
    #         currentTime = millis()
    #         addr = beacon_addr
    #         if (currentTime > PERIODIC_VOICE_TIMER):
    #             PERIODIC_VOICE_TIMER += PERIODIC_VOICE_DELTA_TIME
    #             print(currentTime/1000)
    #
    #             # Voice remove distractors
    #             print("VOICING DISTRACTOR ITEMS")
    #             if (IP_TO_NAME.get(addr)[1] == False):
    #                 voice.distractorPresent()
    #
    #             # Voice required items
    #             print("VOICING REQUIRED ITEMS")
    #             # requiredItemsSet \ itemsOnTable
    #             itemsOnTable_spk = list()
    #             for addr in itemsOnTable:
    #                 itemsOnTable_spk.append(IP_TO_NAME.get(addr)[0])
    #             voice.requires(requiredItemsSet.difference(itemsOnTable))
    #
    #         # Immediate voice cues
    #         if (isItemOnTable):
    #             if (not beacon_addr in itemsOnTable):
    #                 # First added item
    #                 itemsOnTable.add(beacon_addr)
    #                 print("VOICING ADDED ITEM")
    #
    #             else:
    #                 # First removed item
    #                 itemsOnTable.remove(beacon_addr)
    #                 print("VOICING REMOVED ITEM")
    #
    #
    #
    #     trilateration_table.print() if DEBUG_TAB else None



        # Jason code uncomment later 
        # requiredItems = []
        # proceed = True
        # for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
        #     if not beacon_info.required_item:
        #         beaconLocation = beacon_info.LocationEstimate
        #         voice.distractorPresent(beacon_info.name, beaconLocation)
        #         proceed = False
        #         break
        #     else:
        #         requiredItems.add(beacon_info.name)
        # if proceed:
        #     # outputString = ""
        #     # for itemName in requiredItems:
        #     #     outputString = outputString + ", " + itemName
        #     voice.requires(requiredItems)


if __name__ == '__main__':
    main()
