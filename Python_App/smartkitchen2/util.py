import sys
import serial
import threading
from enum import Enum

# Returns list of port names with active devices connected
# @courtesy: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def DiscoverSerialDevices():
    # Windows ports
    if (sys.platform.startswith('win')):
        ports = [f'COM{i}' for i in range(1,256)]
    # Linux devices
    elif sys.platform.startswith('linux'):
        ports = [f'/dev/ttyACM{i}' for i in range(256)]
    # Unsupported OS
    else:
        raise EnvironmentError("Unsupported platform!")
    
    foundDevicePortNames = []
    for port in ports:
        try:
            # If successfully open w/o exception, add port name
            s = serial.Serial(port)
            s.close()
            foundDevicePortNames.append(port)
        except (OSError, serial.SerialException):
            pass
        
    return foundDevicePortNames

def average(array):
        sum = 0
        for el in array:
            sum += el
        return sum / len(array)


class LocationEstimate(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOT_LEFT = 3
    BOT_RIGHT = 4
    OFF = 5
    def __str__(self): 
        # Location estimate, can be directly printed in a string by just passing the object
        # ex.
        # selected_position = Position.TOP_LEFT
        # print(f"You selected {selected_position}") -> prints: You selected top left
        return LocationEstimateToString[self]

LocationEstimateToString = {
    LocationEstimate.TOP_LEFT: "top left",
    LocationEstimate.TOP_RIGHT: "top right",
    LocationEstimate.BOT_LEFT: "bottom left",
    LocationEstimate.BOT_RIGHT: "bottom right",
    LocationEstimate.OFF: "off of the table",
}

class BeaconInfo:
    # Struct / class to deal with beacon information

    def __init__(self, name, is_not_distractor):
        self.rssi_raw_data = [[], [], []] 
        # device_id is an index to its past 3 rssi measurements for this beacon

        self.rssi_array = [None, None, None]
        self.ROLL_AVG_SIZE = 3
        
        self.name = name

        self.required_item = is_not_distractor
        self.loc_estimate = LocationEstimate.OFF

    def add_data(self, device_id, data_point):
        # NOTE: Device should be passed as an int
        # We have this address in our lookup table

        if self.rssi_raw_data[device_id]:
            rssi_values = self.rssi_raw_data[device_id] 
            #Gives us an array of rolling average values for this beacon for this device
            if len(rssi_values) >= self.ROLL_AVG_SIZE:
                # We have met the number of measurements in our rolling average
                rssi_values.pop(0) # remove oldest rssi value from front of array
                rssi_values.append(data_point) # latest rssi value at end of array
            else:
                # We want to add more measurements to our average
                rssi_values.append(data_point)
                
            new_average = average(rssi_values) # Error here -> adding 'int' to NoneType
            self.rssi_raw_data[device_id] = rssi_values
            self.rssi_array[device_id] = round(new_average,2)

        else: # This address hasn't been added to our data table yet
            self.rssi_raw_data[device_id] = [data_point]
            self.rssi_array[device_id] = data_point # Update trilateration table


        return

    def __repr__(self):
        if not self.required_item:
            return f"Distractor {self.name} | {self.rssi_array} "
        else:
            return f"{self.name} | {self.rssi_array}"


class ThreadSafeTrilaterationMap:
    def __init__(self, ip_to_name):
        self.inner_map = {}
        self.lock = threading.Lock()
        self.ip_to_name = ip_to_name

    def put(self, key, value):
        with self.lock:
            self.inner_map[key] = value

    def get(self, key):
        with self.lock:
            return self.inner_map.get(key)

    def delete(self, key):
        with self.lock:
            if key in self.inner_map:
                del self.inner_map[key]

    def print(self):
        print(*[f"{key}: {value}" for key, value in self.inner_map.items()], sep="\n")
    
    # Update value array specifically at scanner_id
    def update_rssi(self, key, rssi_value, scanner_id):
        with self.lock:

            info = self.inner_map.get(
                key,
                BeaconInfo(self.ip_to_name[key][0], self.ip_to_name[key][1]) # Create a new BeaconInfo object if not present
                )
            
            info.add_data(scanner_id, round(rssi_value, 2))
            self.inner_map[key] = info
