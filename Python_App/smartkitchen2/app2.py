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
#   "Placeholder" : ("1 Measure Cup", True),
   "[0]C3:00:00:0B:1A:86" : ("½ Measure Cup", True),
   "[0]C3:00:00:0B:1A:8A" : ("¼ Measure Spoon", True),
  "[0]C3:00:00:0B:1A:88" : ("Calibrator", True),
#   "Placeholder" : ("Stirring Spoon", True),
   "[0]C3:00:00:0B:1A:87" : ("Timer", True),
  "[0]C3:00:00:0B:1A:89" : ("Bowl", True),
#   "Placeholder" : ("Metal Spoon", True),
#   "[0]C3:00:00:0B:1A:XX" : ("Cork Hot Pad", True),
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
        # Check for bounds (must be within BOTH TOP receivers)
        # if (in_bounds[Recv.TOP_LEFT.value] and in_bounds[Recv.TOP_RIGHT.value]):
        #     on_table = True

    elif (Recv.BOT_LEFT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        pos = util.LocationEstimate.BOTTOM
        # Bounds check
        # if (in_bounds[Recv.BOT_LEFT.value] and in_bounds[Recv.BOT_RIGHT.value]):
        #     on_table = True

    elif (Recv.TOP_LEFT in dir_recvs and Recv.BOT_LEFT in dir_recvs):
        pos = util.LocationEstimate.LEFT
        # Bounds check
        # if (in_bounds[Recv.TOP_LEFT.value] and in_bounds[Recv.BOT_RIGHT.value]):
        #     on_table = True

    elif (Recv.TOP_RIGHT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        pos = util.LocationEstimate.RIGHT
        # Bounds check
        # if (in_bounds[Recv.TOP_RIGHT.value] and in_bounds[Recv.BOT_RIGHT.value]):
        #     on_table = True
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
    #calibrate(trilateration_table, 6)

    BEACONIP_TARGET = ['Oatmeal', 'Distractor', 'Timer', 'Salt']
    with open('./drift-data-processed.csv', 'w+') as file:
        count = 0
        while True:
            trilateration_table.print()
            print("\n")
            time.sleep(1)

            if count == 60: break

            for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():
                if beacon_info.name in BEACONIP_TARGET:
                    file.write(beacon_info.name+", "+str(beacon_info.rssi_array[0])+"\n")
                    file.flush()
            count += 1

if __name__ == '__main__':
    main()
