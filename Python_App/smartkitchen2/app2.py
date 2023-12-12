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


class ExprData:
    def __init__(self, expected_loc):
        self.expected_loc = expected_loc

        self.correct_table_region = 0
        self.incorrect_table_region = 0

        self.correct = 0
        self.incorrect = 0

        self.complete = False
        self.num_points = 0

    def toString(self):
        return " Correct: "+str(self.correct)+" Incorrect: "+str(self.incorrect)

    def add_data(self, estimated_loc):

        if self.num_points >= 60:
            self.complete = True
            return

        if (self.expected_loc == util.LocationEstimate.OFF):
            # You expect it to be off the table
            if (estimated_loc == util.LocationEstimate.OFF):
                self.correct +=1
            else: self.incorrect += 1

        else: # You expect it to be on the table
            if (estimated_loc == util.LocationEstimate.OFF):
                self.incorrect +=1
            else: # It is on the table, as expected
                self.correct += 1
                if estimated_loc == self.expected_loc:
                    self.correct_table_region += 1
                else: 
                    self.incorrect_table_region +=1            

        self.num_points += 1

# Clockwise rotation of all items to simulate motion
ESTIMATE_COUNTER = [
     { # state 0, # box at bottom right
    "Salt" : ExprData(util.LocationEstimate.TOP),
    "Oatmeal" : ExprData(util.LocationEstimate.LEFT),
    "Distractor" : ExprData(util.LocationEstimate.RIGHT),
    "Timer" : ExprData(util.LocationEstimate.BOTTOM),
    "Bowl" : ExprData(util.LocationEstimate.OFF),
    },  
    { # state 1, # box at top right
    "Salt" : ExprData(util.LocationEstimate.RIGHT),
    "Oatmeal" : ExprData(util.LocationEstimate.TOP),
    "Distractor" : ExprData(util.LocationEstimate.BOTTOM),
    "Timer" : ExprData(util.LocationEstimate.LEFT),
        "Bowl" : ExprData(util.LocationEstimate.OFF),
    },  
    { # state 2, # box at top left
    "Salt" : ExprData(util.LocationEstimate.BOTTOM),
    "Oatmeal" : ExprData(util.LocationEstimate.RIGHT),
    "Distractor" : ExprData(util.LocationEstimate.LEFT),
    "Timer" : ExprData(util.LocationEstimate.TOP),
        "Bowl" : ExprData(util.LocationEstimate.OFF),
    },
    { # state 3, # box at bottom left
    "Salt" : ExprData(util.LocationEstimate.LEFT),
    "Oatmeal" : ExprData(util.LocationEstimate.BOTTOM),
    "Distractor" : ExprData(util.LocationEstimate.TOP),
    "Timer" : ExprData(util.LocationEstimate.RIGHT),
        "Bowl" : ExprData(util.LocationEstimate.OFF),
    }
    ]

""" HELPER FUNCTIONS """

# Note: calibrate by placing PAN tag in middle of table
def calibrate(trilateration_table, calib_time):
    time.sleep(calib_time) # Wait to get an average going
    rssi_arr = trilateration_table.get(PAN_ADDR).rssi_array
    #trilateration_table.print()

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

    # Blocks for 15 seconds to callibrate the table's RSSI bounds
    calibrate(trilateration_table, 15)

    item_required = None # For saying only one item at a time
    proceed = True

    # CHANGE THIS AS YOU CHANGE THE PHYSICAL SETUP
    EXPR_STATE = 3

    print(ESTIMATE_COUNTER[EXPR_STATE].keys())

    while True:
        trilateration_table.print()
        print("\n")
        time.sleep(1) # Once per second is when we would expect to get updates from all beacons (not at all the case)
        calibrate(trilateration_table,0)  # perform instantaneous calibration

        all_complete = True

        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():

            if not beacon_info:
                print("HOW TF IS BEACON INFO NONTHING HERE")
                print(beacon_addr)
            elif not (beacon_info.name == "Calibrator"):

                (pos, isOnTable) = locate(beacon_addr, trilateration_table)
                beacon_info.loc_estimate = pos
                if not isOnTable:
                    beacon_info.loc_estimate = util.LocationEstimate.OFF
                    pos = util.LocationEstimate.OFF

                # It only adds data points when it is measured as on the table why the fuck

                # EXPERIMENT DATA TRACKING
                if beacon_info.name in ESTIMATE_COUNTER[EXPR_STATE].keys():
                    ESTIMATE_COUNTER[EXPR_STATE][beacon_info.name].add_data(pos)

            # Break out of the loop once we have taken 60 samples for each item
            for (name, data) in ESTIMATE_COUNTER[EXPR_STATE].items():
                if name == beacon_info.name:
                    print(" datapoints "+str(data.num_points))
                    all_complete = all_complete and data.complete

            if all_complete: break



        if all_complete: break


    correct_detection_on_tabletop = 0
    incorrect_detection_on_tabletop = 0
    correct_detection_off_tabletop = 0
    incorrect_detection_off_tabletop = 0

    # Now, out of all items correctly/incorrectly detected on the tabletop
    correct_region_loc_on_tabletop = 0 
    incorrect_region_loc_on_tabletop = 0

    for (name, data) in ESTIMATE_COUNTER[EXPR_STATE].items():
        print(name)
        print(data.toString())

        if data.expected_loc != util.LocationEstimate.OFF:
            correct_detection_on_tabletop += data.correct
            incorrect_detection_off_tabletop += data.incorrect

            correct_region_loc_on_tabletop += data.correct_table_region
            incorrect_region_loc_on_tabletop += data.incorrect_table_region
        else: # if you expect it to be off of the table
            correct_detection_off_tabletop += data.correct
            incorrect_detection_on_tabletop += data.incorrect # why here

    print("Trial outputs: ")
    print("correct_detection_on_table="+str(correct_detection_on_tabletop))
    print("incorrect_detection_on_table="+str(incorrect_detection_on_tabletop))
    print("correct_detection_off_table="+str(correct_detection_off_tabletop))
    print("incorrect_detection_off_table="+str(incorrect_detection_off_tabletop))

    print("correct_region_loc_on_tabletop="+str(correct_region_loc_on_tabletop))
    print("incorrect_region_loc_on_tabletop="+str(incorrect_region_loc_on_tabletop))

    # Outputs: TP, FP, TN, FN





if __name__ == '__main__':
    main()
