from smartkitchen import controller
from smartkitchen import util
from smartkitchen import voice

import pyttsx3

import threading
import time



# Maps ip -> (Name, T=valid item / F=distractor)
IP_TO_NAME = {
    "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
    "[0]C3:00:00:0B:1A:7A": ("Communist Manifesto", True),
    "Placeholder" : ("Salt", True),
    "Placeholder" : ("1 Measure Cup", True),
    "Placeholder" : ("½ Measure Cup", True),
    "Placeholder" : ("¼ Measure Spoon", True),
    "Placeholder" : ("Pan", True),
    "Placeholder" : ("Stirring Spoon", True),
    "Placeholder" : ("Timer", True),
    "Placeholder" : ("Bowl", True),
    "Placeholder" : ("Metal Spoon", True),
    "Placeholder" : ("Cork Hot Pad", True),
}

itemsOnTable = set()
requiredItemsSet = {
    "[0]C3:00:00:0B:1A:7C",
    "[0]C3:00:00:0B:1A:7A"
}

THRESH = -70
DEBUG = True
DEBUG_TAB = False


def millis():
    return time.time() * 1000

def main():
    # Delta timing variables in millis
    PERIODIC_VOICE_DELTA_TIME = 5000  
    PERIODIC_VOICE_TIMER = millis()

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
        # For every item in table
        for (beacon_addr, beacon_info) in trilateration_table.inner_map.items():

            # Update RSSI values between item and all receivers
            sum = 0
            n = 0
            for rssi in beacon_info.rssi_array:
                if rssi:
                    sum += rssi
                    n += 1
            avg = sum / n

            # Determine if item is on table or not
            isItemOnTable = False
            if avg > THRESH:
                isItemOnTable = True
                print(f"{beacon_info.name}: {avg} is on table") if DEBUG else None
            else:
                print(f"{beacon_info.name}: {avg} is not on table") if DEBUG else None

            
            ### VOICE SEQUENCES

            # Periodic voice cues
            currentTime = millis()
            if (currentTime > PERIODIC_VOICE_TIMER):
                PERIODIC_VOICE_TIMER += PERIODIC_VOICE_DELTA_TIME
                print(currentTime/1000)

                # Voice remove distractors
                print("VOICING DISTRACTOR ITEMS")
                if (IP_TO_NAME.get(addr)[1] == False):
                    voice.distractorPresent()

                # Voice required items
                print("VOICING REQUIRED ITEMS")
                # requiredItemsSet \ itemsOnTable
                itemsOnTable_spk = list()
                for addr in itemsOnTable:
                    itemsOnTable_spk.append(IP_TO_NAME.get(addr)[0])
                voice.requires(requiredItemsSet.difference(itemsOnTable))
        

            # Immediate voice cues
            if (isItemOnTable):
                if (not itemsOnTable.contains(beacon_addr)):
                    # First added item
                    itemsOnTable.add(beacon_addr)
                    print("VOICING ADDED ITEM")

                else:
                    # First removed item
                    itemsOnTable.remove(beacon_addr)
                    print("VOICING REMOVED ITEM")
               
            
        
        trilateration_table.print() if DEBUG_TAB else None




if __name__ == '__main__':
    # print("Testing voice")
    # voice.distractorPresent()

    main()
