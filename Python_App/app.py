from smartkitchen import controller
from smartkitchen import util

import threading
import time


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

    print(devices)

    Scanners = []

    for devc in devices:
        print("\n=== Creating a BleuIO receiver instance and thread for "+devc)

        # Scanners.append(controller.Scanner(devc, IP_TO_NAME, trilateration_table, scanner_id))
        # Each scanner will asynchronously do this:
        def scanning_process(scanner_id):
            # Create BleuIO instance
            print("\n=== "+devc+" has started scanning on thread "
            +str(threading.current_thread().name) + " scanner id is "+str(scanner_id))

            Scanner = controller.Scanner(devc, IP_TO_NAME, trilateration_table, scanner_id)
            Scanner.scan()

        scanner_thread = threading.Thread(target=scanning_process, args=(scanner_id,))
        scanner_thread.start()
        scanner_id+=1

    while True:
        time.sleep(1)
        print("Main")
        
        # !!! LOGIC HERE !!!

        THRESH = -70
        DEBUG = True
        DEBUG_TAB = False

        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():

            sum = 0
            n = 0
            for rssi in beacon_info.rssi_array:
                if rssi:
                    sum += rssi
                    n += 1
            avg = sum / n

            # print(f"{beacon_info.name}: {avg}")

            if avg > THRESH:
                print(f"{beacon_info.name}: {avg} is on table") if DEBUG else None
            else:
                print(f"{beacon_info.name}: {avg} is not on table") if DEBUG else None
        
        trilateration_table.print() if DEBUG_TAB else None

main()

