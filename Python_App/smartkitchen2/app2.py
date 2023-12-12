import controller
import util
from util import average
import voice
from server import scan_subscriber

import pyttsx3

import threading
import time

from enum import Enum

class Recv(Enum):
	TOP_LEFT = 3
	BOT_LEFT = 2
	BOT_RIGHT = 1
	TOP_RIGHT = 0
def recv_enum(i):
    for recv in Recv:
        if recv.value == i:
            return recv

# Maps ip -> (Name, T=valid item / F=distractor)
IP_TO_NAME = {
   "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
   "[0]C3:00:00:0B:1A:79": ("Distractor", False),
   "[0]C3:00:00:0B:1A:7B" : ("Salt", True),
   "[0]C3:00:00:0B:1A:86" : ("½ Measure Cup", True),
   "[0]C3:00:00:0B:1A:8A" : ("¼ Measure Spoon", True),
  "[0]C3:00:00:0B:1A:88" : ("Calibrator", True),
   "[0]C3:00:00:0B:1A:87" : ("Timer", True),
  "[0]C3:00:00:0B:1A:89" : ("Bowl", True),
}
PAN_ADDR = "[0]C3:00:00:0B:1A:88"       # temp
TIMER_ADDR = "[0]C3:00:00:0B:1A:87"     # temp
DISTRACT_ADDR = "[0]C3:00:00:0B:1A:79"

THRESH = -70
DEBUG = False
DEBUG_TAB = True

ACTIVATION_MARGIN = 5	# this should be a margin to ignore "noise" in receiver
						# may need a threshold margin per receiver
ON_TABLE_MARGIN = 10     # an margin for determining what is on table (pos --> less strict bounds)
CALIB_RSSI = [0,0,0,0]		# the offset and threshold per RSSI at ith index


EXPECTED_ONTABLE_ESTIMATES = {
    "Salt" : util.LocationEstimate.TOP,
    "Oatmeal" : util.LocationEstimate.LEFT,
    "Distractor" : util.LocationEstimate.RIGHT,
    "Timer" : util.LocationEstimate.BOTTOM 
}

EXPECTED_OFFTABLE_ESTIMATES = {
    "Bowl" : util.LocationEstimate.OFF,
}

ESTIMATE_COUNTER = {
    "Salt" : {
        "Complete": False,
        "Total" : 0,
        "Correct" : 0,
        "Incorrect" : 0
    },
    "Oatmeal" : {
                "Complete": False,
                "Total" : 0,
        "Correct" : 0,
        "Incorrect" : 0
    },
    "Distractor" : {
                "Complete": False,
                "Total" : 0,
        "Correct" : 0,
        "Incorrect" : 0
    },
    "Timer" : {
                "Complete": False,
                "Total" : 0,
        "Correct" : 0,
        "Incorrect" : 0
    },
    "Bowl" : {
        "Complete": False,
        "Total" : 0,
        "Correct" : 0,
        "Incorrect" : 0
    }
}


""" HELPER FUNCTIONS """

# Note: calibrate by placing PAN tag in middle of table
def calibrate(trilateration_table, calib_time):
    time.sleep(calib_time) # Wait to get an average going
    rssi_arr = trilateration_table.get(PAN_ADDR).rssi_array

    for i in range(0,len(rssi_arr)):
        CALIB_RSSI[i] = rssi_arr[i]

        # debug prints
        print(f"{recv_enum(i).name} threshold: {CALIB_RSSI[i] - ON_TABLE_MARGIN}")


def locate(beacon_addr, trilateration_table):
    pos = ""
    on_table = False
    beacon_rssis = trilateration_table.get(beacon_addr).rssi_array

    ## calculate the offset per receiver
    rssi_offsets = []
    for i in range(0,len(beacon_rssis)):
        recv_pair = (beacon_rssis[i] - CALIB_RSSI[i], recv_enum(i))
        rssi_offsets.append(recv_pair)

    ## calculate the bounds
    in_bounds = [beacon_rssis[i] > (CALIB_RSSI[i] - ON_TABLE_MARGIN) for i in range(0,len(beacon_rssis))]
    on_table = sum(in_bounds)>1

    ## determine position
    rssi_offsets_sorted = sorted(rssi_offsets, key=lambda x: x[0], reverse=True)
    dir_recvs = {rssi_offsets_sorted[0][1], rssi_offsets_sorted[1][1]}              # set of first two strongest RSSIs
    if (Recv.TOP_LEFT in dir_recvs and Recv.TOP_RIGHT in dir_recvs):
        pos = util.LocationEstimate.TOP
    elif (Recv.BOT_LEFT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        pos = util.LocationEstimate.BOTTOM
    elif (Recv.TOP_LEFT in dir_recvs and Recv.BOT_LEFT in dir_recvs):
        pos = util.LocationEstimate.LEFT
    elif (Recv.TOP_RIGHT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        pos = util.LocationEstimate.RIGHT
    else:
        pos = util.LocationEstimate.IDK

    ## debug prints
    for i in range(0,len(beacon_rssis)):
        print(f"N:{trilateration_table.get(beacon_addr).name}\tR:{recv_enum(i).name}\tB:{in_bounds[i]}\tOffset:{rssi_offsets[i][0]}")
    print(f"DIRECTION RECEIVERS {dir_recvs}")
    print(f"\n === RESULT: {'On table' if on_table else 'Off table'} {pos}")

    return (pos, on_table)


def main():
    # Maps ip -> BeaconInfo while also performing trilateration logic
    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME)

    scanner_thread = threading.Thread(target=scan_subscriber, args=(trilateration_table,))
    scanner_thread.start()

    # Blocks for 6 seconds to callibrate the table's RSSI bounds
    calibrate(trilateration_table, 6)

    while True:
        trilateration_table.print()
        print("\n")
        time.sleep(1) # Once per second is when we would expect to get updates from all beacons (not at all the case)
        calibrate(trilateration_table,0)  # perform instantaneous calibration

        all_complete = True
        SAMPLES = 60

        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
            
            if beacon_info.name in ESTIMATE_COUNTER.keys() and not ESTIMATE_COUNTER[beacon_info.name]["Complete"]:

                estimated_loc = locate(beacon_addr, trilateration_table)
                expected_loc = None
                if beacon_info.name in EXPECTED_ONTABLE_ESTIMATES.keys:
                    # If its physically on the table, get its expect value from ontable expected
                    expected_loc = EXPECTED_ONTABLE_ESTIMATES[beacon_info.name]
                else: 
                    # Otherwise it must be off the table (ex. Bowl), get expected value from offtable expected
                    expected_loc = EXPECTED_OFFTABLE_ESTIMATES[beacon_info.name]

                if estimated_loc == expected_loc:
                    ESTIMATE_COUNTER[beacon_info.name]["Correct"] += 1
                else:
                    ESTIMATE_COUNTER[beacon_info.name]["Incorrect"] += 1

                ESTIMATE_COUNTER[beacon_info.name]["Total"] += 1
                
                ESTIMATE_COUNTER[beacon_info.name]["Complete"] = (ESTIMATE_COUNTER[beacon_info.name]["Total"]) == SAMPLES


            # Break out of the loop once we have taken 60 samples for each item
            for (name, data) in ESTIMATE_COUNTER.items():
                all_complete = all_complete and ESTIMATE_COUNTER[beacon_info.name]["Complete"]
            if all_complete: break
        
        if all_complete: break

    true_positive = 0
    false_positive = 0
    for name in EXPECTED_ONTABLE_ESTIMATES.keys():
        true_positive += ESTIMATE_COUNTER[name]["Correct"]
        false_positive += ESTIMATE_COUNTER[name]["Incorrect"]

    true_negative = 0
    false_negative = 0
    for name in EXPECTED_OFFTABLE_ESTIMATES.keys():
        true_negative += ESTIMATE_COUNTER[name]["Correct"]
        false_negative += ESTIMATE_COUNTER[name]["Incorrect"]

    print("Trial outputs: ")
    print(true_positive+", "+false_positive+", "+true_negative+", "+false_negative)
    # Outputs: TP, FP, TN, FN





if __name__ == '__main__':
    main()
