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
	BOT_RIGHT = 0
	TOP_RIGHT = 1
def recv_enum(i):
    for recv in Recv:
        if recv.value == i:
            return recv



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

PAN_ADDR = "[0]C3:00:00:0B:1A:88"
ACTIVATION_MARGIN = 5	# this should be a margin to ignore "noise" in receiver
						# may need a threshold margin per receiver
ON_BOUNDARY_MARGIN = 5  # an margin for determining what is on table
CALIB_RSSI = [0,0,0,0]		# the offset and threshold per RSSI at ith index


""" HELPER FUNCTIONS """

# def calibrate_bounds_by_beacon(trilateration_table):
#     time.sleep(6) # Wait to get an average going
#     # Get the distractor BeaconInfo
#     trilateration_table.print()

#     beacon_on_sensor = {
#          0: "[0]C3:00:00:0B:1A:87", # 0 opposite Timer
#          1: "[0]C3:00:00:0B:1A:88", # 1 opposite Pan
#          2: "[0]C3:00:00:0B:1A:79", # 2 opposite Cork hot pad
#          3: "[0]C3:00:00:0B:1A:8A", #3 opposite 1/4 Measure Spoon
#     }
    

#     bounds = [
#          trilateration_table.get(beacon_on_sensor[1]).rssi_array[0],
#          trilateration_table.get(beacon_on_sensor[2]).rssi_array[1],
#          trilateration_table.get(beacon_on_sensor[3]).rssi_array[2],
#          trilateration_table.get(beacon_on_sensor[0]).rssi_array[3]
#     ]
#     # for i in range(0,4):
#     #     bounds.append(trilateration_table.get(beacon_on_sensor[i]).rssi_array[i])

#     avg = average(bounds)
#     for i in range(0,4):
#         bounds[i] = avg
#     trilateration_table.init_bounds(bounds)


# Note: calibrate by placing PAN tag in middle of table
def calibrate(trilateration_table, calib_time):
    time.sleep(calib_time) # Wait to get an average going
    rssi_arr = trilateration_table.get(PAN_ADDR).rssi_array

    for i in range(0,len(rssi_arr)):
        CALIB_RSSI[i] = rssi_arr[i]


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
    in_bounds = [beacon_rssis[i] > CALIB_RSSI[i] for i in range(0,len(beacon_rssis))]

    ## sort list in order of strongest first
    rssi_offsets = sorted(rssi_offsets, key=lambda x: x[0], reverse=True)

    ## determine position
    dir_recvs = {rssi_offsets[0][1], rssi_offsets[1][1]}
    if (Recv.TOP_LEFT in dir_recvs and Recv.TOP_RIGHT in dir_recvs):
        # Top
        pos = "top"
        # Check for bounds (must be within BOTH TOP receivers)
        if (in_bounds[Recv.TOP_LEFT.value] and in_bounds[Recv.TOP_RIGHT.value]):
            on_table = True

    elif (Recv.BOT_LEFT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        # Bottom
        pos = "bottom"
        # Bounds check
        if (in_bounds[Recv.BOT_LEFT.value] and in_bounds[Recv.BOT_RIGHT.value]):
            on_table = True

    elif (Recv.TOP_LEFT in dir_recvs and Recv.BOT_LEFT in dir_recvs):
        # Left
        pos = "left"
        # Bounds check
        if (in_bounds[Recv.TOP_LEFT.value] and in_bounds[Recv.BOT_RIGHT.value]):
            on_table = True

    elif (Recv.TOP_RIGHT in dir_recvs and Recv.BOT_RIGHT in dir_recvs):
        # Right
        pos = "right"
        # Bounds check
        if (in_bounds[Recv.TOP_RIGHT.value] and in_bounds[Recv.BOT_RIGHT.value]):
            on_table = True

    ## debug prints
    for i in range(0,len(beacon_rssis)):
        print(f"R:{recv_enum(i).name}\tB:{in_bounds[i]}\tOffset:{rssi_offsets[i]}")
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
        time.sleep(1)
        calibrate(trilateration_table,0)  # perform instantaneous calibration
        locate(PAN_ADDR, trilateration_table)

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
