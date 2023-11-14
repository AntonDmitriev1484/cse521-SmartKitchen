# from smartkitchen import controller
# from smartkitchen import util

import threading
import time

import numpy as np

# Maps ip -> (Name, T=valid item / F=distractor)
IP_TO_NAME = {
    "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
    "[0]C3:00:00:0B:1A:7A": ("Communist Manifesto", True)
}


def main():
    # List devices
    print("\n=== Finding devices connected to serial port...")
    devices =  util.DiscoverSerialDevices()

    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME)
    
    scanner_id = 0
    for devc in devices:
        print("\n=== Creating a BleuIO receiver instance and thread for "+devc)

        # Each scanner will asynchronously do this:
        def scanning_process(scanner_id):
            # Create BleuIO instance
            print("\n=== "+devc+" has started scanning on thread "
            +str(threading.current_thread().ident) + " scanner id is "+str(scanner_id))

            Scanner = controller.Scanner(devc, IP_TO_NAME, trilateration_table, scanner_id)
            Scanner.scan()

        scanner_thread = threading.Thread(target=scanning_process, args=(scanner_id,))
        scanner_thread.start()
        scanner_id+=1

    while True:
        time.sleep(1)
        print("Main")
        # !!! INSERTION TRILATERATION LOGIC HERE OR IN BEACONINFO !!!
        
        # trilateration_table.print()

# receiver position on table in feet
#               2
#
#   1                       3
#   #   #   #   #   #   #   #
RECEIVER_1_POS = (0,0)
RECEIVER_2_POS = (3,2)
RECEIVER_3_POS = (6,0)
def trilaterate(rssiTable):

    #  key: IP val: ([rssi1, rssi2, rssi3], distance/position stuff) 
    # get intersection points between circles 1,2 and 1,3
    # find intersection point of lines 
    # find intersection between two lines
    # update item's position in table

    # for every item in RSSI table
    for item in rssiTable:
        pass
        
        
        
        
        

def get_item_loc(item_rssis):
    # item_rssis = [rssi_1, rssi_2, rssi_3]

    ### Distances
    item_dists = tuple(map(RSSI_to_dist, item_rssis))

    ### Circle intersections

    # calcuate intersection point(s) between 1,2
    pts12 = circle_intersect(RECEIVER_1_POS[0], RECEIVER_1_POS[1], item_dists[0],
                             RECEIVER_2_POS[0], RECEIVER_2_POS[1], item_dists[1])

    # calculate intersection poin(s)  between 1,3
    pts13 = circle_intersect(RECEIVER_1_POS[0], RECEIVER_1_POS[1], item_dists[0],
                             RECEIVER_3_POS[0], RECEIVER_3_POS[1], item_dists[2])

    ### Line intersections
    item_loc = line_intersect(pts12, pts13)

    return item_loc






def circle_intersect(x0, y0, r0, x1, y1, r1):
    c0 = np.array([x0, y0])
    c1 = np.array([x1, y1])
    v = c1 - c0
    d = np.linalg.norm(v)

    if d > r0 + r1 or d == 0:
        return None
    
    u = v/np.linalg.norm(v)
    xvec = c0 + (d**2 - r1**2 + r0**2)*u/(2*d)

    uperp = np.array([u[1], -u[0]])
    a = ((-d+r1-r0)*(-d-r1+r0)*(-d+r1+r0)*(d+r1+r0))**0.5/d
    return (xvec + a*uperp/2, xvec - a*uperp/2)


def line_intersect(line1, line2):
    # Note: assuming that the lines must intersect (due to our trilateration)
    #       we can set the y-coordinate equal and solve for the x-coordinate
    # general form of line; Ax + By + C = 0
    l1_genconsts = line_general_consts(line1)
    a1 = l1_genconsts[0]
    b1 = l1_genconsts[1]
    c1 = l1_genconsts[2]

    l2_genconsts = line_general_consts(line2)
    a2 = l2_genconsts[0]
    b2 = l2_genconsts[1]
    c2 = l2_genconsts[2]

    x_int = ((b1*c2)-(b2*c1)) / ((a1*b2)-(a2*b1))
    y_int = ((c1*a2-c2*a1)) / ((a1*b2)-(a2*b1))

    return (x_int, y_int)


def line_general_consts(line):
    x1 = line[0][0]
    y1 = line[0][1]
    x2 = line[1][0]
    y2 = line[1][1]

    A = y1 - y2
    B = x2 - x1
    C = (x1 - x2) * y1 + (y2 - y1) * x1

    return (A, B ,C)


MEASURED_RSSI = 10 # need to find RSSI at one meter
ENV_FACT = 2
def RSSI_to_dist(rssi):
    # Distance = 10^((Measured Power - Instant RSSI)/(10*N)).
    exp = (MEASURED_RSSI - rssi)/(10*ENV_FACT)
    return pow(10,exp)

if __name__ == '__main__':

    item_1_rssis = [45.01, 63.02, 52.03]
    get_item_loc(item_1_rssis)

    # main()

