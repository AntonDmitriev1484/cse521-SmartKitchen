from smartkitchen import controller
from smartkitchen import util
from smartkitchen import voice
from flask import Flask, request, jsonify

import pyttsx3

import threading
import time

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

    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME)

    # Defines the Flask server that receives fetch requests from the scanner
    def scan_subscriber():
        app = Flask('ScanSubscriber')
        @app.route('/', methods=['POST'])
        def receive_json():
            try:
                scan = request.get_json()
                print(scan)
                # Still need to maintain its own rolling avg
                # trilateration_table.update_rssi(scan)
                
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        app.run(host='172.27.84.110',port=3000)

            # Updates this scaner's datatable and our threadsafe trilateration_table
    # def update_tables(self, IP_ADDR, RSSI):
    #     if self.is_BLE_beacon(IP_ADDR):
    #         # We have this address in our lookup table
    #         if self.data_table.get(IP_ADDR, None):
    #             (rssi_values, average) = self.data_table[IP_ADDR]

    #             if len(rssi_values) >= self.ROLL_AVG_SIZE:
    #                 # We have met the number of measurements in our rolling average
    #                 rssi_values.pop(0) # remove oldest rssi value from front of array
    #                 rssi_values.append(RSSI) # latest rssi value at end of array
    #             else:
    #                 # We want to add more measurements to our average
    #                 rssi_values.append(RSSI)

    #             new_average = self.average(rssi_values)
    #             self.data_table[IP_ADDR] = (rssi_values, new_average)
    #             self.trilateration_table.update_rssi(IP_ADDR, new_average, self.scanner_id) # Update trilateration table

    #         else: # This address hasn't been added to our data table yet
    #             self.data_table[IP_ADDR] = ([RSSI], RSSI)
    #             self.trilateration_table.update_rssi(IP_ADDR, RSSI, self.scanner_id) # Update trilateration table





    scanner_thread = threading.Thread(target=scan_subscriber)
    scanner_thread.start()

    while True:
        time.sleep(1)        
        # For every item in table

        trilateration_table.print()
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
            addr = beacon_addr
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
                if (not beacon_addr in itemsOnTable):
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