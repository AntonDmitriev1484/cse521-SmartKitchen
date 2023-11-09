from smartkitchen import controller
from smartkitchen import util

import threading

# Command to see all devices:
# 



def main():
    # List devices
    print("\n=== Finding devices connected to serial port...")
    devices =  util.DiscoverSerialDevices()

    # Maps ip -> (Name, T=valid item / F=distractor)
    ip_to_name = {
        "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True)
    }

    trilateration_table = util.ThreadSafeTrilaterationMap()
    
    scanner_id = 0
    for devc in devices:
        print("\n=== Creating a BleuIO receiver instance and thread for "+devc)

        # Each scanner will asynchronously do this:
        def scanning_process():
            # Create BleuIO instance
            print("\n=== "+devc+" has started scanning on thread "+str(threading.current_thread().ident))
            Scanner = controller.Scanner(devc, ip_to_name, trilateration_table, scanner_id)
            Scanner.scan()

        scanner_id+=1

        scanner_thread = threading.Thread(target=scanning_process)
        scanner_thread.start()

main()

